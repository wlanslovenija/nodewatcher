from django import template
from django.template import Library
from django.template import RequestContext
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.conf import settings

register = Library()

DESCRIPTIONS = {
  'up': 'the node is reachable',
  'visible': 'the node is connected to the network but does not reply to ICMP ECHO',
  'down': 'the node is not connected to the network',
  'duped': 'duplicate ICMP ECHO packets have been received',
  'invalid': 'IP address is not allocated but is seen',
  'new': 'the node has just been registered',
  'pending': 'the node has not yet been seen since registration',
  'awaitingrenumber': 'the node has been recently renumbered'
}

IMAGE_TEMPLATE = """<img src="%(media_url)simages/status_%(status)s_%(size)s.png" title="%(title)s" alt="%(status)s" />"""
WRAPPER_TEMPLATE = """<span class="node_status_%(status)s node_status_%(size)s">%(content)s</span>"""

@register.filter
def statusimage(value, arg, autoescape = None):
  value = value.lower()
  if value.endswith("wc"):
    status = value[:-2]
  else:
    status = value

  if not (status in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new', 'awaitingrenumber')):
    return ""
  
  if not (arg in ('big', 'small', 'gmap')):
    arg = "small"
  
  params = {"status" : value, "size" : arg, "title" : ("%s - %s" % (value, DESCRIPTIONS[status])), "media_url" : settings.MEDIA_URL}
  return mark_safe(IMAGE_TEMPLATE % params)

statusimage.needs_autoescape = True

@register.filter
def status(value, arg, autoescape = None):
  value = value.lower()

  if value.endswith("wc"):
    status = value[:-2]
  else:
    status = value

  if not (status in ('up', 'down', 'invalid', 'visible', 'duped', 'pending', 'new', 'awaitingrenumber')):
    return ""
  
  if not (arg in ('big', 'small', 'gmap', 'text')):
    arg = "small"
  
  params = {"status" : value, "size" : arg, "title" : ("%s - %s" % (value, DESCRIPTIONS[status])), "media_url" : settings.MEDIA_URL}
  if arg == 'text':
    params['content'] = value
  else:
    params['content'] = (IMAGE_TEMPLATE % params) + "&nbsp;" + value
  return mark_safe(WRAPPER_TEMPLATE % params)

status.needs_autoescape = True

@register.simple_tag
def statusdesc(value):
  if value.endswith("wc"):
    status = value[:2]
  else:
    status = value

  return DESCRIPTIONS[status]

