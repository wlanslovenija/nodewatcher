from django.db import models

import json_field
import polymorphic
from polymorphic import base as polymorphic_base
from . import polymorphic_deletion_fix, options


class RegistryItemModelBase(polymorphic_base.PolymorphicModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super(RegistryItemModelBase, cls).__new__(cls, name, bases, attrs)

        # Augment the new class with registry options.
        new_class._registry = options.Options(new_class)

        return new_class


class RegistryItemBase(polymorphic.PolymorphicModel):
    """
    An abstract registry configuration item.
    """

    __metaclass__ = RegistryItemModelBase

    # Upon registration, this attribute is replaced with an actual ForeignKey.
    root = None
    # Item display order so that we can load items back from the database in the same
    # order that they were shown on any edit forms.
    display_order = models.IntegerField(null=True, editable=False)
    # Custom item annotations.
    annotations = json_field.JSONField(default={}, editable=False)

    class RegistryMeta:
        registry_id = None

    class Meta:
        abstract = True
        ordering = ['display_order', 'id']

    def get_registry_parent(self):
        """
        Returns the registry parent item instance.
        """

        if not self._registry.has_parent():
            return None

        return getattr(self, self._registry.item_parent_field.name, None)

    def cast(self):
        """
        Casts this registry item into the proper downwards type.
        """

        # TODO: The cast method should not be needed anymore and should be removed
        return self.get_real_instance()

    def save(self, *args, **kwargs):
        """
        Sets up and saves the configuration item.
        """

        super(RegistryItemBase, self).save(*args, **kwargs)

        # If only one configuration instance should be allowed, we should delete existing ones.
        if not self._registry.multiple and self.root:
            cfg, _ = self._registry.registration_point.get_top_level_queryset(
                self.root,
                self._registry.registry_id
            )
            cfg.exclude(pk=self.pk).delete()
