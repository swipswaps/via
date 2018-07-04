import pytest

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse as Response
from werkzeug import wsgi

from via.blocker import Blocker
import StringIO

block_examples = pytest.mark.parametrize('path,blocked, status_code', [
    ('/', False, 200),
    ('/giraf', False, 200),
    ('/giraffe', True, 400),
    ('/giraffe/', True, 400),
    ('/giraffe/neck', True, 400),
    ('/birds', False, 200),
    ('/birds/goose', False, 200),
    ('/birds/duck', True, 451),
    ('/birds/duck/bill', True, 451),
])


class TestBlocker(object):
    def test_serves_template_file(self, client):
        blocker = Blocker(upstream_app,
                          prefixes=[{"prefix": "/baby", "template": "disallow_access.html.jinja2", "status": 451}])
        client = Client(blocker, Response)
        resp = client.get('/baby')
        assert 'Content not available' in resp.data

    @block_examples
    def test_serves_template(self, client, path, blocked, status_code):
        resp = client.get(path)
        if blocked:
            assert resp.data == 'your eyes are protected'
        else:
            assert resp.data == 'scary upstream content'

    @block_examples
    def test_sets_status(self, client, path, blocked, status_code):
        resp = client.get(path)
        assert resp.status_code == status_code

    @block_examples
    def test_sets_mimetype(self, client, path, blocked, status_code):
        resp = client.get(path)
        if blocked:
            assert resp.headers['content-type'].startswith('text/html')
        else:
            assert resp.headers['content-type'].startswith('text/plain')

    @pytest.fixture
    def app(self):
        return Blocker(upstream_app,
                       prefixes=[{"prefix": "/giraffe", "status": 400},
                                 {"prefix": "/birds/duck", "status": 451}],
                       template="your eyes are protected")

    @pytest.fixture
    def client(self, app):
        return Client(app, Response)

@wsgi.responder
def upstream_app(environ, start_response):
    return Response('scary upstream content', mimetype='text/plain')
