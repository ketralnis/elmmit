import os.path

from . import db
from . import models

api_routes = {}


class ApiRoute(object):
    def __init__(self, path, method, doc, fields, db_call, returns):
        assert isinstance(path, str)
        assert method in ['GET', 'POST']
        assert isinstance(path, str)
        assert all(isinstance(name, str) and isinstance(field, Field)
                  for name, field in fields.items())
        assert callable(db_call)

        self.path = path
        self.method = method
        self.doc = doc
        self.fields = fields
        self.db_call = db_call
        self.returns = returns

    @property
    def basename(self):
        return os.path.basename(self.path)

    def __repr__(self):
        return "%s<%s>" % (self.__class__.__name__, self.path)


class Field(object):
    _REQUIRED = []
    def __init__(self, description=None, type=str, default=_REQUIRED):
        self.description = description
        self.type = type
        self.default = default

    @property
    def required(self):
        return self.default is self._REQUIRED


def api_route(path, method, doc, fields, db_call, returns):
    route = ApiRoute(path, method, doc, fields, db_call, returns)
    api_routes[path] = route


api_route('/api/create-author', 'POST',
          'Create a new user account',
          {'author_id': Field('the username of the account to create')},
          db.create_author,
          returns=models.Author)

api_route('/api/get-author', 'GET',
          'Get a user account',
          {'author_id': Field('the username of the account to get')},
          db.get_author,
          returns=models.Author)

api_route('/api/submit-link', 'POST',
          'Submit a new link',
          {'author_id': Field('the author of the link'),
           'title': Field('the title of the link'),
           'url': Field('the URL the link should point to', default=None),
           'body': Field('a textual body of the link', default=None)},
          db.submit_link,
          returns=models.Link)

api_route('/api/get-link', 'GET',
          'Get a link object by ID',
          {'link_id': Field()},
          db.get_link,
          returns=models.Link)

api_route('/api/submit-comment', 'POST',
          'Submit a new comment',
          {'link_id': Field('Which thread this comment belongs to'),
           'author_id': Field('the author of the new comment'),
           'body': Field('the body of the comment. no markup is applied by the server'),
           'parent_id': Field('the comment this new comment is replying to if applicable',
                              default=None)},
          db.submit_comment,
          returns=models.Comment)

api_route('/api/get-comment', 'GET',
          'Get a comment object by ID',
          {'comment_id': Field()},
          db.get_comment,
          returns=models.Comment)

api_route('/api/get-comments-for-link', 'GET',
          'Get all of the comments on a link',
          {'link_id': Field()},
          db.get_comments_for_link,
          returns=models.CommentListing)

LISTING_FIELDS = {
    'pager': Field('null if requesting the first page. otherwise the value you got for the previous page',
                   default=None),
    'limit': Field('how many to request',
                   type=int,
                   default=25),
}

api_route('/api/get-newest-links', 'GET',
          'Get a listing of the youngest links',
          LISTING_FIELDS,
          db.get_newest_links,
          returns=models.LinkListing)

api_route('/api/get-best-links', 'GET',
          'Get the highest scoring links',
          LISTING_FIELDS,
          db.get_best_links,
          returns=models.LinkListing)

api_route('/api/upvote-link', 'POST',
          'Upvote a link',
          {'link_id': Field('the ID of the link to upvote'),
           'diff': Field('how many points to apply',
                         type=int)},
          db.upvote_link,
          returns=models.Link)

api_route('/api/upvote-comment', 'POST',
          'Upvote a comment',
          {'comment_id': Field('the ID of the comment to upvote'),
           'diff': Field('how many points to apply',
                         type=int)},
          db.upvote_comment,
          returns=models.Comment)

