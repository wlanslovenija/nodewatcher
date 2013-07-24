from django import forms
from django.contrib.contenttypes import models as contenttypes_models
from django.core import exceptions
from django.db import models


class RegistryItemBase(models.Model):
    """
    An abstract registry configuration item.
    """

    content_type = models.ForeignKey(contenttypes_models.ContentType, editable=False)

    root = None
    _registry_regpoint = None

    class RegistryMeta:
        registry_id = None

    class Meta:
        abstract = True
        ordering = ['id']

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

            form = DefaultRegistryItemForm

        return form

    @classmethod
    def lookup_path(cls):
        """
        Returns a query filter "path" that can be used for performing root lookups with
        fields that are part of some registry object.
        """

        if cls.__base__ == cls._registry_regpoint.item_base:
            return cls._registry_regpoint.namespace + '_' + cls._meta.app_label + '_' + cls._meta.module_name
        else:
            # TODO: Why is "cls.__base__" passed here to lookup_path? It does not take any arguments.
            return cls.lookup_path(cls.__base__) + '__' + cls._meta.module_name

    @classmethod
    def top_model(cls):
        """
        Returns the top-level model for this registry item.
        """

        if cls.__base__ == cls._registry_regpoint.item_base:
            return cls
        else:
            return cls.__base__.top_model()

    @classmethod
    def can_add(cls, user):
        """
        Returns True if the user has permissions to add this registry item.
        """

        return user.has_perm(
            "%(app_label)s.add_%(module_name)s" % {
                "app_label": cls._meta.app_label,
                "module_name": cls._meta.module_name,
            }
        )

    def cast(self):
        """
        Casts this registry item into the proper downwards type.
        """

        mdl = self.content_type.model_class()
        if mdl == self.__class__:
            return self
        elif mdl is None:
            raise exceptions.ImproperlyConfigured("This configuration object ({0}) is of a class that is not available anymore! If you have recently removed any registry modules, convert your database or reinstall them.".format(self.RegistryMeta.registry_id))

        return mdl.objects.get(pk=self.pk)

    def save(self, *args, **kwargs):
        """
        Sets up and saves the configuration item.
        """

        # Set class identifier
        self.content_type = contenttypes_models.ContentType.objects.get_for_model(self.__class__)
        super(RegistryItemBase, self).save(*args, **kwargs)

        # If only one configuration instance should be allowed, we
        # should delete existing ones
        if not getattr(self.RegistryMeta, 'multiple', False) and self.root:
            cfg, _ = self._registry_regpoint.get_top_level_queryset(self.root, self.RegistryMeta.registry_id)
            cfg.exclude(pk=self.pk).delete()
