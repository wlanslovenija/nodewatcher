from django.views import generic


class Topology(generic.TemplateView):
    template_name = 'topology/topology.html'
