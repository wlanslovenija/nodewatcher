from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.filter
def widthlist(list, width=100):
  """
  Returns width of equally wide columns based on the number of elements in the given list. By default in percent.
  """
  return width / len(list) if len(list) != 0 else 0

@register.filter
def startswith(value, arg):
  """
  Returns True if the given string starts with an argument prefix, otherwise returns False.
  """
  return value.startswith(arg)

class NoticeNode(template.Node):
  def __init__(self, nodelist, var):
    self.nodelist = nodelist
    self.var = var

  def render(self, context):
    return render_to_string('notice.html',
      { 'type' : self.var, 'notice' : self.nodelist.render(context) })

@register.tag
def notice(parser, token):
  """
  Renders notice.
  """
  nodelist = parser.parse(('endnotice',))
  bits = list(token.split_contents())

  if len(bits) > 2 :
    raise TemplateSyntaxError("Only one parameter expected")
  if len(bits) > 1 :
    var = parser.compile_filter(bits[1])
  else:
    var = ""

  parser.delete_first_token()
  return NoticeNode(nodelist, var)
