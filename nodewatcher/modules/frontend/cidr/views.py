from django.views import generic


class Cidr(generic.TemplateView):
    template_name = 'network/cidr.html'
