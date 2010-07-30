from django import template
from django.template import loader

from web.nodes import models

register = template.Library()

@register.inclusion_tag('graph.html', takes_context=True)
def show_graph(context):
  """
  Renders graph template.
  """
  return context

class FullGraphNode(template.Node):
  """
  Renders full graph template based on graph's type.
  """
  def __init__(self, graph):
    self.graph = template.Variable(graph)

  def render(self, context):
    try:
      graph = self.graph.resolve(context)
      return loader.render_to_string(
        'graphs/%s.html' % models.GraphType.as_string(graph.type), {
          'graph' : graph,
        }, context)
    except template.VariableDoesNotExist:
      return ''

@register.tag
def show_full_graph(parser, token):
  args = token.split_contents()
  if len(args) != 2:
      raise TemplateSyntaxError("'show_full_graph' tag requires exactly one argument.")
  return FullGraphNode(args[1])
