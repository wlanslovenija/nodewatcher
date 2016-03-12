from rest_framework import serializers as drf_serializers, viewsets as drf_viewsets

from nodewatcher.core.frontend import api

from . import registration
from .api import views, serializers

# Determine all the top-level models, which contain registration points. All these need
# to be exposed as top-level resources in the API.
top_level_models = set()
for registration_point in registration.all_points():
    top_level_models.add(registration_point.model)

# Create a serializer and a viewset for each model.
for model in top_level_models:
    class meta_cls:
        model = model

    serializer = type(
        '%sRegistryRootSerializer' % (model.__name__),
        (serializers.RegistryRootSerializerMixin, drf_serializers.ModelSerializer),
        {
            'Meta': meta_cls,
        }
    )

    viewset = type(
        '%sRegistryRootViewSet' % (model.__name__),
        (views.RegistryRootViewSetMixin, drf_viewsets.ReadOnlyModelViewSet),
        {
            'queryset': model.objects.all(),
            'serializer_class': serializer,
        }
    )

    # Register the viewset with the API router.
    api.router.register(model._meta.object_name.lower(), viewset)
