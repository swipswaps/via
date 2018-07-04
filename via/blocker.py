from __future__ import unicode_literals

import os

from jinja2 import Environment, FileSystemLoader
from werkzeug import wsgi
from werkzeug.wrappers import BaseResponse as Response

TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../templates/'
PREFIXES = [{"prefix": "/http://nautil.us", "template": "disallow_access.html.jinja2", "status": 451},
            {"prefix": "/http://m.nautil.us", "template": "disallow_access.html.jinja2", "status": 451},
            {"prefix": "/http://m.youtube.com", "template": "could_not_process.html.jinja2", "status": 200},
            {"prefix": "/https://www.youtube.com", "template": "could_not_process.html.jinja2", "status": 200},
            {"prefix": "/http://vimeo.com", "template": "could_not_process.html.jinja2", "status": 200}]


class Blocker(object):

    """
    Blocker is a WSGI middleware that returns a static response when a
    request path matches a list of predefined prefixes.
    """

    def __init__(self, application, prefixes=None, template=None):
        self._application = application
        self._jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR),
                                      trim_blocks=True)
        self._prefixes = prefixes or PREFIXES
        self._template = template

    def __call__(self, environ, start_response):
        for _p in self._prefixes:
            url_to_annotate = wsgi.get_path_info(environ)
            if url_to_annotate.startswith(_p.get('prefix')):
                template = self._template
                if _p.get('template'):
                    template = self._jinja_env.get_template(_p.get('template')).render(url_to_annotate=url_to_annotate[1:])
                resp = Response(template,
                                status=_p['status'], mimetype='text/html')
                return resp(environ, start_response)
        return self._application(environ, start_response)
