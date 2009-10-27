from django import template

register = template.Library()

@register.filter
def widthlist(list, width=100):
  return width / len(list) if len(list) != 0 else 0
