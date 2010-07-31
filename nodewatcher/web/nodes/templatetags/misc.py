# coding=utf-8

import re

from django import template
from django.template import loader, defaultfilters
from django.utils import text

register = template.Library()

DASH_START_END_RE = re.compile(r'^-+|-+$')
HEADING_REPLACE = (
  (u'đ', u'd'),
  (u'Đ', u'D'),
)

@register.filter
def startswith(value, arg):
  """
  Returns True if the given string starts with an argument prefix, otherwise returns False.
  """
  return value.startswith(arg)

@register.filter
def anchorify(anchor):
  """
  Convert string to suitable for anchor id.
  """
  anchor = defaultfilters.striptags(anchor)
  anchor = text.unescape_entities(anchor)
  for a, b in HEADING_REPLACE:
    anchor = anchor.replace(a, b)
  anchor = defaultfilters.slugify(anchor)
  anchor = DASH_START_END_RE.sub('', anchor)
  if not anchor or not anchor[0].isalpha():
    anchor = 'a' + anchor 
  return anchor

@register.inclusion_tag('heading.html', takes_context=True)
def heading(context, level, heading, classes=None):
  """
  Renders heading with anchor id.
  """
  anchor = base_anchor = anchorify(heading)
  i = 0
  while anchor in context.render_context:
    anchor = base_anchor + "-" + unicode(i)
    i += 1
  context.render_context[anchor] = True
  return {
    'level'   : level,
    'heading' : heading,
    'id'      : anchor,
    'classes' : classes,
  }

class SetContextNode(template.Node):
  """
  This class defines renderer which just updates current template context with the rendered output of the block inside tags.
  """
  def __init__(self, nodelist, variable):
    self.nodelist = nodelist
    self.variable = variable
  
  def render(self, context):
    context[self.variable] = self.nodelist.render(context)
    return ''

@register.tag
def setcontext(parser, token):
  """
  Sets (updates) current template context with the rendered output of the block inside tags.
  """
  nodelist = parser.parse(('endsetcontext',))
  args = list(token.split_contents())
  
  if len(args) != 3 or args[1] != "as":
    raise TemplateSyntaxError("%r expected format is 'as name'" % args[0])
  variable = args[2]
  
  parser.delete_first_token()
  
  return SetContextNode(nodelist, variable)

class NoticeNode(template.Node):
  """
  This class defines notice renderer.
  """
  def __init__(self, nodelist, notice_type, classes):
    self.nodelist = nodelist
    self.notice_type = notice_type
    self.classes = classes

  def render(self, context):
    return loader.render_to_string(
      'notice.html', {
        'type' : self.notice_type.resolve(context),
        'classes' : self.classes.resolve(context),
        'notice' : self.nodelist.render(context),
      }, context)

@register.tag
def notice(parser, token):
  """
  Renders notice.
  """
  nodelist = parser.parse(('endnotice',))
  args = list(token.split_contents())

  if len(args) > 3:
    raise TemplateSyntaxError("'notice' tag requires at most two arguments.")
  classes = args[2] if len(args) > 2 else '""'
  notice_type = args[1] if len(args) > 1 else '""'
  
  parser.delete_first_token()
  
  notice_type = parser.compile_filter(notice_type)
  classes = parser.compile_filter(classes)
  
  return NoticeNode(nodelist, notice_type, classes)
