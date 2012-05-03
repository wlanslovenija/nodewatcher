# coding=utf-8

import re

from django import template
from django.conf import settings
from django.template import loader, defaultfilters
from django.utils import safestring
from django.utils import text

register = template.Library()

DASH_START_END_RE = re.compile(r'^-+|-+$')
HEADING_REPLACE = (
  (u'đ', u'd'),
  (u'Đ', u'D'),
)
DOCUMENTATION_LINKS = getattr(settings, 'DOCUMENTATION_LINKS', {})

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
    raise template.TemplateSyntaxError("'%s' tag expected format is 'as name'" % args[0])
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
    raise template.TemplateSyntaxError("'%s' tag requires at most two arguments" % args[0])
  classes = args[2] if len(args) > 2 else '""'
  notice_type = args[1] if len(args) > 1 else '""'
  
  parser.delete_first_token()
  
  notice_type = parser.compile_filter(notice_type)
  classes = parser.compile_filter(classes)
  
  return NoticeNode(nodelist, notice_type, classes)

class DoclinkNode(template.Node):
  """
  This class defines doclink renderer.
  """
  def __init__(self, tag, link, var_name):
    self.tag = tag
    self.link = link
    self.var_name = var_name

  def render(self, context):
    html = loader.render_to_string(
      'documentation_link.html', {
        'url' : DOCUMENTATION_LINKS.get(self.tag),
        'link' : self.link.resolve(context),
      }, context).strip()
    
    if self.var_name:
      context[self.var_name] = safestring.mark_safe(html)
      return ''
    else:
      return html

@register.tag
def doclink(parser, token):
  """
  Renders documentation link.
  """
  args = list(token.split_contents())

  if len(args) != 3 and len(args) != 5:
    raise template.TemplateSyntaxError("'%s' tag takes two or four arguments" % args[0])
  tag = args[1]
  link = parser.compile_filter(args[2])
  var_name = None
  if len(args) == 5:
    if args[3] != "as":
      raise template.TemplateSyntaxError("'%s' tag expected third argument is 'as'" % args[0])
    var_name = args[4]
  
  return DoclinkNode(tag, link, var_name)
