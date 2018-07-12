import pytest

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse as Response
from werkzeug import wsgi

from via.blocker import Blocker

block_examples = pytest.mark.parametrize('path,blocked,status_code,msg', [
    ('/', False, 200, ''),
    ('/http://giraf.com', False, 200, 'scary upstream content'),
    ('/http://giraffe.com', True, 400, 'disallow access'),
    ('/http://giraffe.com/', True, 400, 'disallow access'),
    ('/http://giraffe.com/neck', True, 400, 'disallow access'),
    ('/http://bird.com', False, 200, 'scary upstream content'),
    ('/http://birds.com', True, 451, 'cannot be annotated'),
    ('/https://birds.com', True, 451, 'cannot be annotated'),
    ('/birds.com', True, 451, 'cannot be annotated'),
    ('/giraffe.com', True, 400, 'disallow access'),
    ('/bird.com', False, 200, 'scary upstream content'),
    ('/giraff.com', False, 200, 'scary upstream content'),
])


class TestBlocker(object):
    @block_examples
    def test_serves_template(self, client, path, blocked, status_code, msg):
        resp = client.get(path)
        assert msg in resp.data

    @block_examples
    def test_sets_status(self, client, path, blocked, status_code, msg):
        resp = client.get(path)
        assert resp.status_code == status_code

    @block_examples
    def test_sets_mimetype(self, client, path, blocked, status_code, msg):
        resp = client.get(path)
        if blocked:
            assert resp.headers['content-type'].startswith('text/html')
        else:
            assert resp.headers['content-type'].startswith('text/plain')

    @pytest.fixture
    def app(self):
        return Blocker(upstream_app,
                       domains=[{"domain": "giraffe.com", "template": "disallow_access.html.jinja2", "status": 400},
                                {"domain": "birds.com", "template": "could_not_process.html.jinja2", "status": 451}])

    @pytest.fixture
    def client(self, app):
        return Client(app, Response)


@wsgi.responder
def upstream_app(environ, start_response):
    return Response('scary upstream content', mimetype='text/plain')
