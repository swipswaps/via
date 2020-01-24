from StringIO import StringIO

import mock
import pytest
from werkzeug import wsgi
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse as Response

from via.blocker import Blocker

# Simulated response from the proxied website, returned if the content is not blocked.
UPSTREAM_CONTENT = "the upstream content"

# The MIME type associated with `UPSTREAM_CONTENT`. This should be different
# than the "text/html" type returned for error pages indicating blocked content,
# so that tests can verify that the expected `Content-Type` header was returned
# depending on whether the page was blocked.
UPSTREAM_MIME_TYPE = "text/plain"

# Tests for blocked and non-blocked responses.
# These assume the default blocklist (via/default-blocklist.txt).
block_examples = pytest.mark.parametrize(
    "path,blocked,status_code,msg",
    [
        # Requests with no domain in the path.
        ("/", False, 200, ""),
        # Non-blocked requests.
        ("/giraffe.com", False, 200, UPSTREAM_CONTENT),
        ("/http://giraffe.com", False, 200, UPSTREAM_CONTENT),
        ("/https://giraffe.com", False, 200, UPSTREAM_CONTENT),
        ("/https://giraffe.com/foobar", False, 200, UPSTREAM_CONTENT),
        # A domain blocked for legal reasons.
        ("/nautil.us", True, 451, "disallow access"),
        # Different variations of a blocked domain.
        ("/www.youtube.com", True, 200, "cannot be annotated"),
        ("/http://www.youtube.com", True, 200, "cannot be annotated"),
        ("/https://www.youtube.com", True, 200, "cannot be annotated"),
        ("/https://www.youtube.com/foobar", True, 200, "cannot be annotated"),
    ],
)


class FakeFile(object):
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return StringIO(self.content)

    def __exit__(self, type, value, traceback):
        pass


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
            assert resp.headers["content-type"].startswith("text/html")
        else:
            assert resp.headers["content-type"].startswith(UPSTREAM_MIME_TYPE)

    def test_it_reads_blocklist_from_file(self, file_open, file_stat):
        blocklist_path = "/tmp/custom_blocklist.txt"
        file_open.return_value = FakeFile("timewaster.com blocked")
        app = Blocker(upstream_app, blocklist_path)
        client = Client(app, Response)

        # The blocklist should be fetched when the app is instantiated.
        file_open.assert_called_with(blocklist_path)

        # Fetch a site that is blocked in the custom blocklist.
        resp = client.get("/timewaster.com")
        assert "cannot be annotated" in resp.data

        # Fetch a site that is not blocked in the custom blocklist,
        resp = client.get("/youtube.com")
        assert UPSTREAM_CONTENT in resp.data

    def test_it_rereads_blocklist_if_mtime_changes(self, client, file_open, file_stat):
        blocklist_path = "/tmp/custom_blocklist.txt"
        file_open.return_value = FakeFile("")
        app = Blocker(upstream_app, blocklist_path)
        client = Client(app, Response)

        # An initial request should not re-read the blocklist file,
        # as the mtime is unchanged.
        file_open.reset_mock()

        resp = client.get("/timewaster.com")

        file_open.assert_not_called()
        assert UPSTREAM_CONTENT in resp.data

        # Simulate a change in content and mtime of the blocklist file, which
        # should cause it to be re-read on the next request.
        file_open.return_value = FakeFile("timewaster.com blocked")
        file_stat.return_value.st_mtime = 200

        resp = client.get("/timewaster.com")

        file_open.assert_called_with(blocklist_path)
        assert "cannot be annotated" in resp.data

    def test_it_ignores_invalid_lines_in_blocklist(self, file_open):
        file_open.return_value = FakeFile(
            """
timewaster.com blocked
invalid-line
foo bar baz

# This is a comment
"""
        )
        app = Blocker(upstream_app)
        client = Client(app, Response)

        resp = client.get("/timewaster.com")
        assert "cannot be annotated" in resp.data

    @pytest.fixture
    def file_open(self):
        with mock.patch("via.blocker.open") as mock_open:
            yield mock_open

    @pytest.fixture
    def file_stat(self):
        with mock.patch("via.blocker.os.stat") as stat_mock:
            stat_mock.st_mtime = 100
            yield stat_mock

    @pytest.fixture
    def app(self, file_stat):
        return Blocker(upstream_app)

    @pytest.fixture
    def client(self, app):
        return Client(app, Response)


@wsgi.responder
def upstream_app(environ, start_response):
    return Response(UPSTREAM_CONTENT, mimetype=UPSTREAM_MIME_TYPE)
