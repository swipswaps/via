from __future__ import unicode_literals

from urllib import urlencode
from urlparse import parse_qsl


def pop_query_params_with_prefix(environ, prefix):
    """
    Extract and remove query string parameters beginning with ``prefix``.

    :param environ: WSGI environ dict
    :param prefix: Prefix to match
    :return: A dict of query param / value pairs
    """
    orig_qs = environ['QUERY_STRING']
    parsed_query_items = parse_qsl(orig_qs, keep_blank_values=True)
    popped_params = {}
    updated_query_items = []

    for key, value in parsed_query_items:
        if key.startswith(prefix):
            popped_params[key] = value
        else:
            updated_query_items.append((key, value))

    updated_qs = urlencode(updated_query_items)
    environ['QUERY_STRING'] = updated_qs
    environ['REQUEST_URI'] = environ['REQUEST_URI'][:-len(orig_qs)] + updated_qs

    return popped_params


class ConfigExtractor(object):
    """
    WSGI middleware which extracts client configuration params from the URL.

    Client configuration is supplied via "via."-prefixed query parameters,
    which are removed from the URL passed along to the proxy server.

    These parameters are then used to populate the parameters exposed to
    rendered templates.
    """

    def __init__(self, application):
        self._application = application

    def __call__(self, environ, start_response):
        template_params = environ.get('pywb.template_params', {})

        via_params = pop_query_params_with_prefix(environ, 'via.')
        if 'via.request_config_from_frame' in via_params:
            template_params['h_request_config'] = via_params['via.request_config_from_frame']
        if 'via.open_sidebar' in via_params:
            template_params['h_open_sidebar'] = True

        environ['pywb.template_params'] = template_params

        return self._application(environ, start_response)
