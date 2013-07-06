from django.views.generic import base

class NewNode(base.TemplateView):
    template_name = 'nodes/new.html'

class EditNode(base.TemplateView):
    template_name = 'nodes/edit.html'
