# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from math import floor

from django import template
from django.template import Context
from django.template.loader import get_template

from ..forms import (
    render_button, render_field, render_field_and_label, render_form,
    render_form_group, render_formset, 
    render_label, render_form_errors, render_formset_errors
)

from .. import (
    render_icon, render_alert, parse_token_contents
)

register = template.Library()


@register.simple_tag
def theme_formset(*args, **kwargs):
    """
    Render a formset


    **Tag name**::

        theme_formset

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_formset formset %}

    **example**::

        {% theme_formset formset layout='horizontal' %}

    """
    return render_formset(*args, **kwargs)


@register.simple_tag
def theme_formset_errors(*args, **kwargs):
    """
    Render formset errors

    **Tag name**::

        theme_formset_errors

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_formset_errors formset %}

    **example**::

        {% theme_formset_errors formset layout='inline' %}
    """
    return render_formset_errors(*args, **kwargs)


@register.simple_tag
def theme_form(*args, **kwargs):
    """
    Render a form

    **Tag name**::

        theme_form

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_form form %}

    **example**::

        {% theme_form form layout='inline' %}
    """
    return render_form(*args, **kwargs)


@register.simple_tag
def theme_form_errors(*args, **kwargs):
    """
    Render form errors

    **Tag name**::

        theme_form_errors

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_form_errors form %}

    **example**::

        {% theme_form_errors form layout='inline' %}
    """
    return render_form_errors(*args, **kwargs)


@register.simple_tag
def theme_field(*args, **kwargs):
    """
    Render a field

    **Tag name**::

        theme_field

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_field form_field %}

    **example**::

        {% theme_field form_field %}
    """
    return render_field(*args, **kwargs)


@register.simple_tag()
def theme_label(*args, **kwargs):
    """
    Render a label

    **Tag name**::

        theme_label

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_label FIXTHIS %}

    **example**::

        {% theme_label FIXTHIS %}
    """
    return render_label(*args, **kwargs)


@register.simple_tag
def theme_button(*args, **kwargs):
    """
    Render a button

    **Tag name**::

        theme_button

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% theme_button FIXTHIS %}

    **example**::

        {% theme_button FIXTHIS %}
    """
    return render_button(*args, **kwargs)


@register.simple_tag
def theme_icon(icon, **kwargs):
    """
    Render an icon

    **Tag name**::

        theme_icon

    **Parameters**:

        :icon: icon name

    **usage**::

        {% theme_icon "icon_name" %}

    **example**::

        {% theme_icon "star" %}

    """
    return render_icon(icon, **kwargs)


@register.simple_tag
def theme_alert(content, type='info', dismissable=True):
    """
    Render an alert

    **Tag name**::

        theme_alert

    **Parameters**:

        :content: HTML content of alert
        :type: one of 'info', 'warning', 'danger' or 'success'
        :dismissable: boolean, is alert dismissable

    **usage**::

        {% theme_alert "my_content" %}

    **example**::

        {% theme_alert "Something went wrong" type='error' %}

    """
    return render_alert(content, type, dismissable)

@register.simple_tag
def theme_legend(content):
    """
    Render a legend

    **Tag name**::

        theme_title

    **Parameters**:

        :content: HTML content
        
    **usage**::

        {% theme_legend "my_content" %}

    **example**::

        {% theme_legend "Title" %}

    """
    return "<legend>%s</legend>" % content

@register.tag('buttons')
def theme_buttons(parser, token):
    """
    Render buttons for form

    **Tag name**::

        theme_buttons

    **Parameters**:

        :parser:
        :token:

    **usage**::

        {% theme_buttons FIXTHIS %}

    **example**::

        {% theme_buttons FIXTHIS %}
    """
    kwargs = parse_token_contents(parser, token)
    kwargs['nodelist'] = parser.parse(('endbuttons', ))
    parser.delete_first_token()
    return ButtonsNode(**kwargs)


class ButtonsNode(template.Node):

    def __init__(self, nodelist, args, kwargs, asvar, **kwargs2):
        self.nodelist = nodelist
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        output_kwargs = {}
        for key in self.kwargs:
            output_kwargs[key] = handle_var(self.kwargs[key], context)
        buttons = []
        submit = output_kwargs.get('submit', None)
        reset = output_kwargs.get('reset', None)
        if submit:
            buttons.append(theme_button(submit, 'submit'))
        if reset:
            buttons.append(theme_button(reset, 'reset'))
        buttons = ' '.join(buttons) + self.nodelist.render(context)
        output_kwargs.update({
            'label': None,
            'field': buttons,
        })
        output = render_form_group(render_field_and_label(**output_kwargs))
        if self.asvar:
            context[self.asvar] = output
            return ''
        else:
            return output

@register.tag('alert')
def theme_alert(parser, token):
    """
    Render buttons for form

    **Tag name**::

        alert

    **Parameters**:

        :parser:
        :token:

    **usage**::

        {% alert type %} ...  {% endalert %}

    **example**::

        {% alert %} ... {% endalert %}
    """
    #kwargs = parse_token_contents(parser, token)
    kwargs = {}
    kwargs['dismissable'] = False
    kwargs['type'] = False
    kwargs['nodelist'] = parser.parse(('endalert', ))
    parser.delete_first_token()
    return AlertNode(**kwargs)

class AlertNode(template.Node):

    def __init__(self, nodelist, type="info", icon=None, dismissable=False):
        self.nodelist = nodelist
        self.alert_type = type
        self.icon = icon
        self.dismissable = dismissable

    def render(self, context):
        return render_alert(self.nodelist.render(context), alert_type=self.alert_type, dismissable=self.dismissable)

@register.simple_tag(takes_context=True)
def theme_messages(context, *args, **kwargs):
    """
    Show django.contrib.messages Messages in Bootstrap alert containers.

    In order to make the alerts dismissable (with the close button),
    we have to set the jquery parameter too when using the
    theme_javascript tag.

    **Tag name**::

        theme_messages

    **Parameters**:

        :context:
        :args:
        :kwargs:

    **usage**::

        {% theme_messages FIXTHIS %}

    **example**::

        {% theme_messages FIXTHIS %}

    """
    return get_template('form/messages.html').render(context)
