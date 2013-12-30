from django.views import generic


class NodesList(generic.TemplateView):
    template_name = 'nodes/list.html'
