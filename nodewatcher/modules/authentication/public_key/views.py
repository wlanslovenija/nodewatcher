from django.core import urlresolvers
from django.contrib.auth import decorators as auth_decorators
from django.views import generic
from django.utils import decorators as django_decorators

from nodewatcher.core.frontend import views

from . import models


class AddPublicKey(views.CancelableFormMixin, generic.CreateView):
    template_name = 'public_key/new.html'
    model = models.UserAuthenticationKey
    fields = ['name', 'public_key']

    @django_decorators.method_decorator(auth_decorators.login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddPublicKey, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddPublicKey, self).form_valid(form)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class RemovePublicKey(views.CancelableFormMixin, generic.DeleteView):
    template_name = 'public_key/remove.html'
    model = models.UserAuthenticationKey

    @django_decorators.method_decorator(auth_decorators.login_required)
    def dispatch(self, *args, **kwargs):
        return super(RemovePublicKey, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return super(RemovePublicKey, self).get_queryset().filter(user=self.request.user)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class ListPublicKeys(generic.TemplateView):
    template_name = 'public_key/list_public_keys.html'
