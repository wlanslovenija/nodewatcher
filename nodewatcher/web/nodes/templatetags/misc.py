from django import template
from django.template import loader

register = template.Library()

@register.filter
def startswith(value, arg):
  """
  Returns True if the given string starts with an argument prefix, otherwise returns False.
  """
  return value.startswith(arg)

class NoticeNode(template.Node):
  def __init__(self, nodelist, notice_type, classes):
    self.nodelist = nodelist
    self.notice_type = template.Variable(notice_type)
    self.classes = template.Variable(classes)

  def render(self, context):
    try:
      return loader.render_to_string(
        'notice.html', {
          'type' : self.notice_type.resolve(context),
          'classes' : self.classes.resolve(context),
          'notice' : self.nodelist.render(context),
        }, context)
    except template.VariableDoesNotExist:
      return ''

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
  
  return NoticeNode(nodelist, notice_type, classes)
