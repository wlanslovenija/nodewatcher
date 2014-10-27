from django.views import generic


class Map(generic.TemplateView):
    template_name = 'map/map.html'
