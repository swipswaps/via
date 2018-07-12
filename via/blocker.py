from __future__ import unicode_literals

import os

from jinja2 import Environment, FileSystemLoader
from werkzeug import wsgi
from werkzeug.wrappers import BaseResponse as Response
from urlparse import urlparse

TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../templates/'
DOMAINS = [{"domain": "nautil.us", "template": "disallow_access.html.jinja2", "status": 451},
           {"domain": "m.nautil.us", "template": "disallow_access.html.jinja2", "status": 451},
           {"domain": "m.youtube.com", "template": "could_not_process.html.jinja2", "status": 200},
           {"domain": "www.youtube.com", "template": "could_not_process.html.jinja2", "status": 200},
           {"domain": "vimeo.com", "template": "could_not_process.html.jinja2", "status": 200}]


class Blocker(object):

    """
    Blocker is a WSGI middleware that returns a static response when a
    request path matches a list of predefined domains.
    """

    def __init__(self, application, domains=None):
        self._application = application
        self._jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR),
                                      trim_blocks=True)
        self._domains = domains or DOMAINS

    def __call__(self, environ, start_response):
        url_to_annotate = wsgi.get_path_info(environ)[1:]
        parsed_url = urlparse(url_to_annotate)

        if not parsed_url.scheme:
            url_to_annotate = "http://" + url_to_annotate
            parsed_url = urlparse(url_to_annotate)

        hostname_to_annotate = parsed_url.hostname

        for _d in self._domains:
            if hostname_to_annotate and hostname_to_annotate == _d['domain']:
                template = self._jinja_env.get_template(_d['template']).render(url_to_annotate=url_to_annotate)
                resp = Response(template,
                                status=_d['status'], mimetype='text/html')
                return resp(environ, start_response)
        return self._application(environ, start_response)
