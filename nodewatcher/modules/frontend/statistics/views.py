from django.views import generic


class NetworkStatistics(generic.TemplateView):
    template_name = 'network/statistics.html'
