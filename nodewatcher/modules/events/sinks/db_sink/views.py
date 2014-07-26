from django.views import generic


class EventsList(generic.TemplateView):
    template_name = 'events/list.html'
