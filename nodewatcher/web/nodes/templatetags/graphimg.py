from django import template

register = template.Library()

@register.inclusion_tag('graph.html', takes_context=True)
def show_graph(context):
  """
  Renders graph template.
  """
  return context
