from __future__ import absolute_import, unicode_literals

import urllib
import urlparse

from django import template

try:
    from django.http.request import QueryDict
except ImportError:  # django 1.4.2
    from django.http import QueryDict

from django.utils.encoding import iri_to_uri

register = template.Library()


@register.simple_tag
def url_add_params(url, **kwargs):
    r = urlparse.urlparse(url)
    query = QueryDict(r.query, mutable=True)
    try:
        for key, val in kwargs.iteritems():
            if hasattr(val, '__iter__'):
                query.setlist(key, val)
            else:
                query[key] = val
        query_string = query.urlencode()
        if query_string:
            query_string = '?%s' % query_string
        fragment = r.fragment and '#%s' % iri_to_uri(r.fragment) or ''
        return '%s%s%s' % (
            iri_to_uri(r.path),
            query_string,
            fragment
        )
    except:
        return ''
