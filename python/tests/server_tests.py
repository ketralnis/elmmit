import json
import os.path
import shutil
import tempfile
import unittest

from elmmit import server

class TestDb(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

        self.app = server.app
        self.app.testing = True
        self.app.config['db_path'] = os.path.join(self.tempdir, 'db.db')

        self.client = self.app.test_client()
        print self.app

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        del self.tempdir

    def test_server_basics(self):
        # since everything is auto-generated, as long as a basic get and a post
        # mostly work then we can trust the tests in db_tests.py
        rv = self.client.post('/api/create-author',
                              data={'author_id': 'hello'})
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data)['author_id'],
                         'hello')

        rv = self.client.get('/api/get-author?author_id=hello')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data)['author_id'],
                         'hello')

        rv = self.client.post('/api/submit-link',
                              data={'author_id': 'hello',
                                    'title': 'a title',
                                    'url': 'a url'})
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get('/api/get-newest-links')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('links', json.loads(rv.data))

