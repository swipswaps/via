from __future__ import unicode_literals

from urlparse import urlparse, urljoin

import cgi
import jinja2

from pywb.webapp.live_rewrite_handler import RewriteHandler
from pywb.rewrite.url_rewriter import UrlRewriter as BaseUrlRewriter
from pywb.framework.wbrequestresponse import WbResponse


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates/", encoding="utf-8-sig")
)


class TemplateRewriteHandler(RewriteHandler):
    def __init__(self, config):
        super(TemplateRewriteHandler, self).__init__(config)

        self.templates = config.get("templates", {})

    def _make_response(self, wbrequest, status_headers, gen, is_rewritten):
        # only redirect for non-identity and non-embeds
        if not wbrequest.wb_url.is_embed and not wbrequest.wb_url.is_identity:
            content_type = status_headers.get_header("Content-Type")
            cleaned_content_type = _lookup_key(content_type)
            tpl_name = self.templates.get(cleaned_content_type)

            if tpl_name is not None:
                tpl = env.get_template(tpl_name)
                tpl_params = {"url": wbrequest.wb_url.url}
                tpl_params.update(wbrequest.env.get("pywb.template_params", {}))
                result = tpl.render(**tpl_params)
                return WbResponse.text_response(
                    result.encode("utf-8-sig"), content_type=b"text/html; charset=utf-8"
                )

        return super(TemplateRewriteHandler, self)._make_response(
            wbrequest, status_headers, gen, is_rewritten
        )


class UrlRewriter(BaseUrlRewriter):
    """
    URL rewriter invoked by pywb to rewrite references to URLs in proxied pages.

    The base implementation in pywb rewrites all URLs to go through the proxy.

    Every URL that is proxied adds overhead to the Via service and also slows
    down the page load for the user, as resources are much slower if served
    through the proxy than a local CDN.

    :param url: The URL string to rewrite. This may be absolute or relative.
    :param mod: A hint about the context in which the URL is used
    """
    def rewrite(self, url, mod=None):
        # `url` may be absolute or relative. Convert to absolute if necessary.
        if _is_absolute_url(url):
            abs_url = url
        else:
            abs_url = urljoin(self.wburl.url, url)

        # Don't proxy resources loaded as media files or that appear to be media
        # files based on their extension.
        if mod in ["im_", "oe_"] or _has_extension(abs_url, MEDIA_EXTENSIONS):
            return abs_url

        # Don't proxy iframes.
        if mod in ["if_"]:
            return abs_url

        # Don't proxy scripts.
        if mod in ["js_"] or _has_extension(abs_url, SCRIPT_EXTENSIONS):
            return abs_url

        # Don't rewrite URLs that refer to other origins.
        if _url_origin(abs_url) != _url_origin(self.wburl.url):
            return abs_url

        # Rewrite the URL, which will make it go through the proxy.
        return super(UrlRewriter, self).rewrite(url, mod)


MEDIA_EXTENSIONS = [
    # Image files
    b".gif",
    b".jpg",
    b".jpeg",
    b".ico",
    b".png",
    b".svg",

    # Video files
    b".webm",

    # Audio files
    b".mp3",
    b".mp4",

    # Fonts
    b".woff",
    b".woff2",
]

SCRIPT_EXTENSIONS = [b".js"]


def _has_extension(url, extensions):
    parsed_url = urlparse(url)
    for ext in extensions:
        if parsed_url.path.endswith(ext):
            return True
    return False


def _url_origin(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


def _is_absolute_url(url):
    return (
        url.startswith(b"http:") or url.startswith(b"https:") or url.startswith(b"//")
    )


def _lookup_key(val):
    try:
        type_, params = cgi.parse_header(val)
    except TypeError:
        return val
    else:
        return type_
