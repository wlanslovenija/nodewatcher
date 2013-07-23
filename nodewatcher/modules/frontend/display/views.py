from django.views import generic


class DisplayNode(generic.TemplateView):
    template_name = 'nodes/display.html'
