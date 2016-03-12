from rest_framework import viewsets

FIELD_SEPARATOR = '|'


class RegistryRootViewSetMixin(object):
    def get_queryset(self):
        queryset = super(RegistryRootViewSetMixin, self).get_queryset()
        return self.get_registry_queryset(queryset)

    def get_registry_queryset(self, queryset):
        for field in self.request.query_params.getlist('fields'):
            field_name, queryset = apply_registry_field(field, queryset)
        return queryset


def apply_registry_field(field_specifier, queryset):
    """
    Applies a given registry field specifier to the given queryset.

    :param field_specifier: Field specifier string
    :param queryset: Queryset to apply the field specifier to
    :return: An updated queryset
    """

    atoms = field_specifier.split(FIELD_SEPARATOR)
    field_name = None

    # Parse registry point.
    if atoms:
        registry_point = atoms.pop(0)
        queryset = queryset.regpoint(registry_point)

    # Parse registry item identifier.
    if atoms:
        registry_id = atoms.pop(0)

        # Parse optional field path specifier.
        field_path = ''
        if atoms:
            field_path = atoms.pop(0)

        field_name = '%s%s%s' % (registry_point, registry_id.replace('.', '_'), field_path.replace('.', '_'))
        queryset = queryset.registry_fields(**{field_name: '%s%s' % (registry_id, ('#%s' % field_path) if field_path else '')})

    return field_name, queryset
