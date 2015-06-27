# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from django.conf import settings
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from django.forms.widgets import flatatt


THEME_DEFAULTS = {
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-10',
    'required_css_class': '',
    'error_css_class': 'has-error',
    'success_css_class': 'has-success',
    'formset_renderers': {
        'default': 'nodewatcher.core.frontend.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'nodewatcher.core.frontend.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'nodewatcher.core.frontend.renderers.FieldRenderer',
        'inline': 'nodewatcher.core.frontend.renderers.InlineFieldRenderer',
    },
}


def get_theme_setting(setting, default=None):
    """
    Read a setting
    """
    return THEME_DEFAULTS.get(setting, default)


def get_renderer(renderers, **kwargs):
    layout = kwargs.get('layout', '')
    path = renderers.get(layout, renderers['default'])
    mod, cls = path.rsplit(".", 1)
    return getattr(import_module(mod), cls)


def get_formset_renderer(**kwargs):
    renderers = get_theme_setting('formset_renderers')
    return get_renderer(renderers, **kwargs)


def get_form_renderer(**kwargs):
    renderers = get_theme_setting('form_renderers')
    return get_renderer(renderers, **kwargs)


def get_field_renderer(**kwargs):
    renderers = get_theme_setting('field_renderers')
    return get_renderer(renderers, **kwargs)


def text_value(value):
    """
    Force a value to text, render None as an empty string
    """
    if value is None:
        return ''
    return force_text(value)


def text_concat(*args, **kwargs):
    """
    Concatenate several values as a text string with an optional separator
    """
    separator = text_value(kwargs.get('separator', ''))
    values = filter(None, [text_value(v) for v in args])
    return separator.join(values)


def split_css_classes(css_classes):
    """
    Turn string into a list of CSS classes
    """
    classes_list = text_value(css_classes).split(' ')
    return [c for c in classes_list if c]


def add_css_class(css_classes, css_class, prepend=False):
    """
    Add a CSS class to a string of CSS classes
    """
    classes_list = split_css_classes(css_classes)
    classes_to_add = [c for c in split_css_classes(css_class)
                      if c not in classes_list]
    if prepend:
        classes_list = classes_to_add + classes_list
    else:
        classes_list += classes_to_add
    return ' '.join(classes_list)


def remove_css_class(css_classes, css_class):
    """
    Remove a CSS class from a string of CSS classes
    """
    remove = set(split_css_classes(css_class))
    classes_list = [c for c in split_css_classes(css_classes)
                    if c not in remove]
    return ' '.join(classes_list)


def render_tag(tag, attrs=None, content=None, close=True):
    """
    Render a HTML tag
    """
    builder = '<{tag}{attrs}>{content}'
    if content or close:
        builder += '</{tag}>'
    return builder.format(
        tag=tag,
        attrs=flatatt(attrs) if attrs else '',
        content=text_value(content),
    )


def render_icon(icon, title=''):
    """
    Render a Bootstrap glyphicon icon
    """
    attrs = {
        'class': 'glyphicon glyphicon-{icon}'.format(icon=icon),
    }
    if title:
        attrs['title'] = title
    return '<span{attrs}></span>'.format(attrs=flatatt(attrs))


def render_alert(content, alert_type=None, dismissable=True):
    """
    Render a Bootstrap alert
    """
    button = ''
    if not alert_type:
        alert_type = 'info'
    css_classes = ['alert', 'alert-' + text_value(alert_type)]
    if dismissable:
        css_classes.append('alert-dismissable')
        button = '<button type="button" class="close" ' + \
                 'data-dismiss="alert" aria-hidden="true">&times;</button>'
    return '<div class="{css_classes}">{button}{content}</div>'.format(
        css_classes=' '.join(css_classes),
        button=button,
        content=text_value(content),
    )
