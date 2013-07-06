from django.views.generic import base

class DisplayNode(base.TemplateView):
    template_name = 'nodes/display.html'
