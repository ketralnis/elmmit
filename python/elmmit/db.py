from collections import namedtuple
from functools import wraps
import json
import sqlite3
import sys
import time

from . import utils
from . models import Author, Comment, Link
from . models import LinkListing, CommentListing

def connect_db(fname):
    conn = sqlite3.connect(fname)

    conn.executescript("""
        PRAGMA auto_vacuum=INCREMENTAL;
        PRAGMA busy_timeout=2000;
        PRAGMA encoding="UTF-8";
        PRAGMA foreign_keys=true;
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS authors (
            author_id NOT NULL PRIMARY KEY,
            created NOT NULL DEFAULT (strftime('%s','now')),
            karma INTEGER NOT NULL DEFAULT 0
        ) WITHOUT ROWID;

        CREATE TABLE IF NOT EXISTS links (
            link_id NOT NULL PRIMARY KEY,
            author_id NOT NULL REFERENCES authors(author_id),
            created INTEGER NOT NULL DEFAULT (strftime('%s','now')),
            title TEXT NOT NULL,
            url TEXT NULL,
            body TEXT NULL,
            points INTEGER NOT NULL DEFAULT (0)
        ) WITHOUT ROWID;
        CREATE INDEX IF NOT EXISTS links_by_author ON links(author_id);
        CREATE INDEX IF NOT EXISTS links_by_points ON links(points DESC);

        CREATE TABLE IF NOT EXISTS comments (
            comment_id NOT NULL PRIMARY KEY,
            link_id NOT NULL REFERENCES links(link_id),
            author_id NOT NULL REFERENCES authors(author_id),
            created INTEGER NOT NULL DEFAULT (strftime('%s','now')),
            parent_id NULL REFERENCES comments(comment_id),
            body TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT (0)
        ) WITHOUT ROWID;
        CREATE INDEX IF NOT EXISTS comments_by_author ON comments(author_id);
        CREATE INDEX IF NOT EXISTS comments_by_link ON comments(link_id);
    """)
    conn.row_factory = sqlite3.Row

    return conn


class Pager(object):
    """Representation of an opaque cursor

    Queries that return listings also return one of these strings so that
    further calls can retrieve the next page of results

    Note: the implementation uses sqlite's OFFSET operator which is very slow
    on large datasets
    """

    def __init__(self, offset):
        self.offset = offset

    @classmethod
    def parse(cls, blob):
        if not blob:
            return cls(offset=0)
        try:
            offset = json.loads(utils.debase64(blob))['offset']
            return cls(offset=offset)
        except Exception:
            return cls(offset=0)

    def unparse(self):
        return utils.enbase64(json.dumps({'offset': self.offset}))


def transaction(fn):
    @wraps(fn)
    def _fn(conn, *a, **kw):
        if isinstance(conn, sqlite3.Cursor):
            # if we're already in a transaction, just pass it along
            return fn(conn, *w, **kw)
        else:
            with conn:
                # otherwise start one and pass that in instead
                curs = conn.cursor()
                return fn(curs, *a, **kw)
    return _fn


@transaction
def create_author(conn, author_id):
    "Create the given author ID if it doesn't exist"

    # a note on author_ids: we let the user specify the author_id with capital
    # letters if they want, but we always use the lower-case version in the
    # database. We use the canonical downcased version of their name for the
    # foreign keys, so it's also not possible to change a username after it has
    # been created

    conn.execute("INSERT OR IGNORE INTO authors(author_id) VALUES(lower(?))",
                (author_id,))
    return get_author(conn, author_id)


def get_author(conn, author_id):
    "Find the given author by name"

    rows = conn.execute(
        """
        SELECT *
        FROM authors WHERE author_id = lower(?)
        """,
        (author_id,))

    return Author(**rows.fetchone())


@transaction
def submit_link(conn, author_id, title, url, body, created=None):
    link_id = utils.uuid4_36()
    created = int(created or time.time())
    conn.execute(
        """
        INSERT INTO links(link_id, author_id, title, url, body, created)
        VALUES(?, lower(?), ?, ?, ?, ?)
        """,
        (link_id, author_id, title, url, body, created))
    return get_link(conn, link_id)


def get_link(conn, link_id):
    rows = conn.execute(
        """
        SELECT *
        FROM links
        WHERE link_id=?
        """,
        (link_id,))
    return Link(**rows.fetchone())


@transaction
def submit_comment(conn, link_id, author_id, body, parent_id=None):
    comment_id = utils.uuid4_36()

    if parent_id is not None:
        parent = get_comment(conn, parent_id)
        if parent.link_id != link_id:
            raise ValueError("Comments with parents must belong to the same link")

    conn.execute(
        """
        INSERT INTO comments(comment_id, link_id, author_id, body, parent_id)
        VALUES(?, ?, lower(?), ?, ?)
        """,
        (comment_id, link_id, author_id, body, parent_id or None))
    return get_comment(conn, comment_id)


def get_comment(conn, comment_id):
    rows = conn.execute(
        """
        SELECT *
        FROM comments
        WHERE comment_id=?
        """,
        (comment_id,))
    return Comment(**rows.fetchone())


def get_comments_for_link(conn, link_id):
    """
    Get all of the comments for a given link.

    No pagination, sorting, or tree-building is done
    """

    rows = conn.execute(
        """
        SELECT *
        FROM comments
        WHERE link_id=?
        """,
        (link_id,))
    return CommentListing(comments=[Comment(**row) for row in rows])


def get_newest_links(conn, pager, limit=25):
    """
    Get the `limit` youngest links

    Returns a tuple `(links, cursor)` where `cursor` is either None or a string
    that can be used to fetch the next page of results
    """
    rows, next_pager = _paginate(
        conn,
        """
        SELECT *
        FROM links
        ORDER BY created DESC
        """,
        (),
        pager,
        limit)
    return LinkListing(links=[Link(**row) for row in rows], pager=next_pager)


def get_best_links(conn, pager, limit=25):
    """
    Get the `limit` highest scored links

    Returns a tuple `(links, cursor)` where `cursor` is either None or a string
    that can be used to fetch the next page of results
    """
    rows, next_pager = _paginate(
        conn,
        """
        SELECT *
        FROM links
        ORDER BY points DESC
        """,
        (),
        pager,
        limit)
    return LinkListing(links=[Link(**row) for row in rows],
                       pager=next_pager)


def _paginate(conn, query, params, pager, limit):
    # helper function for our pageable queries since they all look the same

    # take our opaque cursor and parse it
    pager = Pager.parse(pager)

    # take the query and add our LIMIT & OFFSET portions. fetch one more than
    # the limit so we know if there are any entries on the next page or not
    rows = conn.execute(query + " LIMIT ? OFFSET ?",
                        params + (limit+1, pager.offset))
    rows = list(rows)

    next_pager = None
    if len(rows) > limit:
        next_pager = Pager(offset=pager.offset+limit).unparse()
        rows = rows[:-1]

    return rows, next_pager


@transaction
def upvote_link(curs, link_id, diff=1):
    """
    Change the score of a link by `diff` points

    Credits the author's karma appropriately
    """
    curs.execute(
        """
        UPDATE links SET points = points + ?
        WHERE link_id=?
        """,
        (diff, link_id))
    link = get_link(curs, link_id)
    _increment_karma(curs, link.author_id, diff)
    return get_link(curs, link_id)


@transaction
def upvote_comment(curs, comment_id, diff=1):
    """
    Change the score of a comment by `diff` points

    Credits the author's karma appropriately
    """
    curs.execute(
        """
        UPDATE comments SET points = points + ?
        WHERE comment_id=?
        """,
        (diff, comment_id))
    comment = get_comment(curs, comment_id)
    _increment_karma(curs, comment.author_id, diff)
    return get_comment(curs, comment_id)


def _increment_karma(curs, author_id, diff):
    # we should always be appearing in someone else's transaction
    assert isinstance(curs, sqlite3.Cursor)

    curs.execute("UPDATE authors SET karma = karma + ? WHERE author_id=lower(?)",
                 (diff, author_id,))

