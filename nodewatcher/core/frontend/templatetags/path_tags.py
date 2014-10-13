import os

from django import template
from django.template import defaultfilters

register = template.Library()


@register.filter(name='basename')
@defaultfilters.stringfilter
def basename(path):
    return os.path.basename(path)
