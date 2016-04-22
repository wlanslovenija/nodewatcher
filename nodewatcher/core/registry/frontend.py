from rest_framework import serializers as drf_serializers, viewsets as drf_viewsets

from nodewatcher.core.api import urls as api_urls, serializers as api_serializers

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
        base_view = 'apiv2:%s-list' % model._meta.object_name.lower()

    serializer = type(
        '%sRegistryRootSerializer' % (model.__name__),
        (
            api_serializers.JSONLDSerializerMixin,
            serializers.RegistryRootSerializerMixin,
            drf_serializers.ModelSerializer
        ),
        {
            'Meta': meta_cls,
        }
    )

    # Register the serializer with the API serializer pool.
    api_serializers.pool.register(serializer)

    viewset = type(
        '%sViewSet' % (model.__name__),
        (views.RegistryRootViewSetMixin, drf_viewsets.ReadOnlyModelViewSet),
        {
            'queryset': model.objects.all(),
            'serializer_class': serializer,
        }
    )

    # Register the viewset with the API router.
    api_urls.v2_api.register(model._meta.object_name.lower(), viewset)
