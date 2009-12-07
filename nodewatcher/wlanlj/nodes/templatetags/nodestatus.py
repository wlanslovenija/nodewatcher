from django import template
from django.template import Library
from django.template import RequestContext
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = Library()

DESCRIPTIONS = {
  'up': 'node is reachable',
  'visible': 'node is visible via OLSR but does not reply to ICMP ECHO',
  'down': 'node is not visible via OLSR',
  'duped': 'duplicate ICMP ECHO packets have been received',
  'invalid': 'IP is not allocated but is seen',
  'new': 'node has just been registered',
  'pending': 'node has not yet been seen since registration',
  'awaitingrenumber': 'node has been recently renumbered'
}

IMAGE_TEMPLATE = """<img src="/images/status_%(status)s_%(size)s.png" title="%(title)s" alt="%(status)s"/>"""
WRAPPER_TEMPLATE = """<span class="node_status_%(status)s node_status_%(size)s">%(content)s</span>"""

def statusimage(value, arg, autoescape = None):
  value = value.lower()
  
  if not (value in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new', 'awaitingrenumber')):
    return ""
  
  if not (arg in ('big', 'small', 'gmap')):
    arg = "small"
  
  params = {"status" : value, "size" : arg, "title" : ("%s - %s" % (value, DESCRIPTIONS[value]))}
  return mark_safe(IMAGE_TEMPLATE % params)

def status(value, arg, autoescape = None):
  value = value.lower()
  
  if not (value in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new', 'awaitingrenumber')):
    return ""
  
  if not (arg in ('big', 'small', 'gmap')):
    arg = "small"
  
  params = {"status" : value, "size" : arg, "title" : ("%s - %s" % (value, DESCRIPTIONS[value]))}
  params['content'] = (IMAGE_TEMPLATE % params) + "&nbsp;" + value
  return mark_safe(WRAPPER_TEMPLATE % params)

@register.simple_tag
def statusdesc(value):
  return DESCRIPTIONS[value]

status.needs_autoescape = True
statusimage.needs_autoescape = True

register.filter('statusimage', statusimage)
register.filter('status', status)
