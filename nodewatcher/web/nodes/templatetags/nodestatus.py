from django import template
from django.template import Library
from django.template import RequestContext
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = Library()

IMAGE_TEMPLATE = """<img src="/images/status_%(status)s_%(size)s.png" title="%(status)s" alt="%(status)s"/>"""

WRAPPER_TEMPLATE = """<span class="node_status_%(status)s node_status_%(size)s">%(content)s</span>"""

def statusimage(value, arg, autoescape=None):

    value = value.lower()

    if not (value in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new')):
      return ""

    if not (arg in ('big', 'small', 'gmap')):
      arg = "small"

    params = {"status":value, "size":arg}

    return mark_safe(IMAGE_TEMPLATE % params)

def status(value, arg, autoescape=None):

    value = value.lower()

    if not (value in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new')):
      return ""

    if not (arg in ('big', 'small', 'gmap')):
      arg = "small"

    params = {"status":value, "size":arg}

    params['content'] = (IMAGE_TEMPLATE % params) + "&nbsp;" + value

    return mark_safe(WRAPPER_TEMPLATE % params)

status.needs_autoescape = True
statusimage.needs_autoescape = True

register.filter('statusimage', statusimage)

register.filter('status', status)

