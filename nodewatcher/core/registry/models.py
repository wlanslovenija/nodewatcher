from django import forms

import polymorphic
from . import polymorphic_deletion_fix


class RegistryItemBase(polymorphic.PolymorphicModel):
    """
    An abstract registry configuration item.
    """

    root = None
    _registry_regpoint = None

    class RegistryMeta:
        registry_id = None

    class Meta:
        abstract = True
        ordering = ['id']

    @classmethod
    def get_registry_regpoint(self):
        """
        Returns the registration point this registry item belongs to.
        """

        return self._registry_regpoint

    @classmethod
    def get_form(cls):
        """
        Returns the form used for this model.
        """

        form = getattr(cls, '_forms', {}).get(cls, None)

        if form is None:
            class DefaultRegistryItemForm(forms.ModelForm):
                class Meta:
                    model = cls
                    fields = '__all__'

            form = DefaultRegistryItemForm

        return form

    @classmethod
    def get_registry_lookup_chain(cls):
        """
        Returns a query filter "chain" that can be used for performing root lookups with
        fields that are part of some registry object.
        """

        if cls.__base__ == cls._registry_regpoint.item_base:
            return cls._registry_regpoint.namespace + '_' + cls._meta.app_label + '_' + cls._meta.model_name
        else:
            for base in cls.__bases__:
                if hasattr(base, 'get_registry_lookup_chain'):
                    return base.get_registry_lookup_chain() + '__' + cls._meta.model_name

    @classmethod
    def get_registry_id(cls):
        """
        Returns the item's registry identifier.
        """

        return cls.RegistryMeta.registry_id

    @classmethod
    def get_registry_toplevel(cls):
        """
        Returns the toplevel item for its registry id.
        """

        return cls._registry_regpoint.get_top_level_class(cls.get_registry_id())

    @classmethod
    def has_registry_multiple(cls):
        """
        Returns true if the item's registry id can contain multiple items.
        """

        return getattr(cls.RegistryMeta, 'multiple', False)

    @classmethod
    def is_registry_multiple_static(cls):
        """
        Returns true if the item's registry id can contain multiple items and
        should always contain all the possible items.
        """

        return getattr(cls.RegistryMeta, 'multiple_static', False)

    @classmethod
    def has_registry_parent(cls):
        """
        Returns true if the item has a parent.
        """

        return hasattr(cls, '_registry_object_parent')

    def get_registry_parent(self):
        """
        Returns the registry parent item instance.
        """

        if not self.has_registry_parent():
            return None

        return getattr(self, self._registry_object_parent_link.name, None)

    @classmethod
    def has_registry_children(cls):
        """
        Returns true if the item has children.
        """

        return getattr(cls, '_registry_has_children', False)

    @classmethod
    def is_registry_toplevel(cls):
        """
        Returns true if the item is a toplevel item for its registry id.
        """

        return cls.__base__ == cls._registry_regpoint.item_base

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

        # If only one configuration instance should be allowed, we
        # should delete existing ones
        if not getattr(self.RegistryMeta, 'multiple', False) and self.root:
            cfg, _ = self._registry_regpoint.get_top_level_queryset(self.root, self.RegistryMeta.registry_id)
            cfg.exclude(pk=self.pk).delete()
