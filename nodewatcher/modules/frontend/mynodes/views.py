from django.utils import decorators
from django.views import generic

from nodewatcher.extra.accounts import decorators as accounts_decorators


@decorators.method_decorator(accounts_decorators.authenticated_required, name='dispatch')
class MyNodesList(generic.TemplateView):
    template_name = 'nodes/mynodes.html'
