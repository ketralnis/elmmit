from collections import namedtuple

class Model(object):
    def __init__(self, **kw):
        assert all(k in self.fields for k in kw)
        self.data = kw

    def __getattr__(self, name):
        return self.data[name]

    def to_json(self):
        return self.data

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           ', '.join(["%s=%r" % (field, self.data[field])
                                     for field in self.fields]))


class Author(Model):
    fields = 'author_id created karma'.split()


class Link(Model):
    fields = 'link_id author_id created title url body points'.split()


class Comment(Model):
    fields = 'comment_id link_id author_id created parent_id body points'.split()


class LinkListing(Model):
    fields = 'links pager'.split(' ')

    def to_json(self):
        return {'links': map(Link.to_json, self.links),
                'pager': self.pager}


class CommentListing(Model):
    fields = ['comments']

    def to_json(self):
        return {'comments': map(Comment.to_json, self.comments)}

