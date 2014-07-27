from django.views import generic


class MyNodesList(generic.TemplateView):
    template_name = 'nodes/mynodes.html'
