from rest_framework import fields, relations


class IntraRegistryForeignKeyField(fields.Field):
    def __init__(self, *args, **kwargs):
        self.related_model = kwargs.pop('related_model')
        super(IntraRegistryForeignKeyField, self).__init__(*args, **kwargs)

    def get_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        return {
            '@id': '_:%s' % self.related_model._registry.get_api_id(value.pk),
        }
