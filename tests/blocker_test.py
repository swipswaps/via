import pytest

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse as Response
from werkzeug import wsgi

from via.blocker import Blocker

block_examples = pytest.mark.parametrize('path,blocked, status_code', [
    ('/', False, 200),
    ('/http://giraf.com', False, 200),
    ('/http://giraffe.com', True, 400),
    ('/http://giraffe.com/', True, 400),
    ('/http://giraffe.com/neck', True, 400),
    ('/http://bird.com', False, 200),
    ('/http://birds.com', True, 451),
    ('/https://birds.com', True, 451),
    ('/birds.com', True, 451),
    ('/giraffe.com', True, 400),
    ('/bird.com', False, 200),
    ('/giraff.com', False, 200),
])


class TestBlocker(object):
    def test_serves_template_file(self, client):
        blocker = Blocker(upstream_app,
                          domains=[{"domain": "baby.com", "template": "disallow_access.html.jinja2", "status": 451}])
        client = Client(blocker, Response)
        resp = client.get('/baby.com')
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
                       domains=[{"domain": "giraffe.com", "status": 400},
                                {"domain": "birds.com", "status": 451}],
                       template="your eyes are protected")

    @pytest.fixture
    def client(self, app):
        return Client(app, Response)


@wsgi.responder
def upstream_app(environ, start_response):
    return Response('scary upstream content', mimetype='text/plain')
