import time
import unittest

from elmmit import db

class TestDb(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect_db(':memory:')

    def test_create_user(self):
        author = db.create_author(self.conn, 'David')
        self.assertEqual(author.author_id, "david")

    def test_submit_link(self):
        author = db.create_author(self.conn, 'David')
        link = db.submit_link(self.conn, author.author_id, 'a title', 'a url', 'the body')
        self.assertTrue(db.get_link(self.conn, link.link_id).title,
                        link.title)

    def test_create_comment_root(self):
        author = db.create_author(self.conn, 'David')
        link = db.submit_link(self.conn, author.author_id, 'a title', 'a url', 'the body')
        comment = db.submit_comment(self.conn,
                                    link.link_id,
                                    author.author_id,
                                    "a body")
        self.assertEqual(db.get_comment(self.conn, comment.comment_id).body,
                         comment.body)

    def test_submit_comment_child(self):
        author = db.create_author(self.conn, 'David')
        link = db.submit_link(self.conn, author.author_id, 'a title', 'a url', 'the body')
        parent_comment = db.submit_comment(self.conn,
                                           link.link_id,
                                           author.author_id,
                                           "a body")
        child_comment = db.submit_comment(self.conn,
                                          link.link_id,
                                          author.author_id,
                                          "a body",
                                          parent_id=parent_comment.comment_id)
        self.assertEqual(db.get_comment(self.conn, child_comment.comment_id).parent_id,
                         child_comment.parent_id,
                         parent_comment.comment_id)

        comments = db.get_comments_for_link(self.conn, link.link_id)
        ids = set(c.comment_id for c in comments)
        self.assertEqual(ids,
                         set([parent_comment.comment_id,
                              child_comment.comment_id]))

    def test_upvote_comment(self):
        author = db.create_author(self.conn, 'David')
        link = db.submit_link(self.conn, author.author_id, 'a title', 'a url', 'the body')
        comment = db.submit_comment(self.conn,
                                    link.link_id,
                                    author.author_id,
                                    "a body")

        db.upvote_comment(self.conn, comment.comment_id, diff=5)
        self.assertEqual(db.get_comment(self.conn, comment.comment_id).points,
                         5)
        self.assertEqual(db.get_author(self.conn, author.author_id).karma,
                         5)

    def test_link_listings(self):
        author = db.create_author(self.conn, 'david')

        test_links = 10

        all_links = [db.submit_link(self.conn,
                                    author.author_id,
                                    'title #%d' % (i,),
                                    'http://www.google.com?q=%d' % (i,),
                                    'body #%d' % (i,),
                                    created=time.time()+i)
                     for i in range(test_links)]

        # upvote them in reverse creation order so the highest-upvoted is the
        # oldest. that way get_newest_links and get_best_links will have
        # different results
        all_links = [db.upvote_link(self.conn, link.link_id, diff=i)
                     for i, link in enumerate(reversed(all_links))]

        # make sure the author got their rightful karma
        self.assertGreater(db.get_author(self.conn, author.author_id).karma, 1)

        # make sure the query results look the way we expect them to (testing
        # pagination while we're at it)

        # sorted by created time
        self.assertEqual(
            [l.link_id for l in sorted(all_links,
                                       key=lambda l: l.created,
                                       reverse=True)],
            [l.link_id for l in self._follow_pagination(db.get_newest_links)])

        # sorted by best
        self.assertEqual(
            [l.link_id for l in sorted(all_links,
                                       key=lambda l: l.points,
                                       reverse=True)],
            [l.link_id for l in self._follow_pagination(db.get_best_links)])


    def _follow_pagination(self, db_fn):
        pager = None

        while True:
            links, pager = db_fn(self.conn, pager=pager, limit=25)
            for link in links:
                yield link
            if pager is None:
                break
