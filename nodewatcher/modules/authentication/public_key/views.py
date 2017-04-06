from django.core import urlresolvers
from django.views import generic

from rest_framework import filters, viewsets

from nodewatcher.core.frontend import views
from nodewatcher.extra.accounts import mixins

from . import permissions, models, serializers


class AddPublicKey(mixins.AuthenticatedRequiredMixin, views.CancelableFormMixin, generic.CreateView):
    template_name = 'public_key/new.html'
    model = models.UserAuthenticationKey
    fields = ['name', 'public_key']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddPublicKey, self).form_valid(form)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class RemovePublicKey(mixins.AuthenticatedRequiredMixin, views.CancelableFormMixin, generic.DeleteView):
    template_name = 'public_key/remove.html'
    model = models.UserAuthenticationKey

    def get_queryset(self):
        return super(RemovePublicKey, self).get_queryset().filter(user=self.request.user)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class ListPublicKeys(mixins.AuthenticatedRequiredMixin, generic.TemplateView):
    template_name = 'public_key/list_public_keys.html'


class UserAuthenticationKeyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for user authentication keys.
    """

    queryset = models.UserAuthenticationKey.objects.all()
    serializer_class = serializers.UserAuthenticationKeySerializer
    permission_classes = (permissions.UserAuthenticationKeyPermission,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ['id', 'name', 'fingerprint', 'created']

    def get_queryset(self):
        """
        Filter user authentication keys for the currently authenticated user.
        """

        qs = super(UserAuthenticationKeyViewSet, self).get_queryset()
        user = self.request.user
        if not user.is_authenticated():
            return qs.none()

        qs = qs.filter(user=user)
        return qs
