from django.views import generic


class IpSpace(generic.TemplateView):
    template_name = 'network/ip_space.html'
