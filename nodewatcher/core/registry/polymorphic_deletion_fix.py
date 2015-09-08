import six
import types

from django.db.models import deletion


# We need to patch the collector as otherwise cascade deletion of polymorphic models fails.
# See: https://code.djangoproject.com/ticket/23076
# See: https://github.com/django/django/pull/2940
# TODO: Find a better way to fix deletion of polymorphic models.
class PolymorphicCollector(deletion.Collector):
    def add(self, objs, source=None, nullable=False, reverse_dependency=False):
        """
        Adds 'objs' to the collection of objects to be deleted.  If the call is
        the result of a cascade, 'source' should be the model that caused it,
        and 'nullable' should be set to True if the relation can be null.

        Returns a list of all objects that were not already collected.
        """
        if not objs:
            return []
        new_objs = []

        if source is not None:
            source = source._meta.concrete_model
        concrete_model_objs = {}

        for obj in objs:
            model = obj.__class__
            concrete_model = model._meta.concrete_model
            concrete_model_objs.setdefault(concrete_model, {})
            concrete_model_objs[concrete_model].setdefault(model, [])
            concrete_model_objs[concrete_model][model].append(obj)

        for concrete_model, model_objs in six.iteritems(concrete_model_objs):
            for model, objs in six.iteritems(model_objs):
                instances = self.data.setdefault(model, set())
                for obj in objs:
                    if obj not in instances:
                        new_objs.append(obj)
                instances.update(new_objs)

            # Nullable relationships can be ignored -- they are nulled out before
            # deleting, and therefore do not affect the order in which objects have
            # to be deleted.
            if source is not None and not nullable:
                if reverse_dependency:
                    source_, concrete_model_ = concrete_model, source
                else:
                    concrete_model_, source_ = concrete_model, source
                self.dependencies.setdefault(source_, set()).add(concrete_model_)

        return new_objs

    def add_field_update(self, field, value, objs):
        """
        Schedules a field update. 'objs' must be a homogeneous iterable
        collection of model instances (e.g. a QuerySet).
        """
        if not objs:
            return

        concrete_model_objs = {}
        for obj in objs:
            model = obj.__class__
            concrete_model = model._meta.concrete_model
            concrete_model_objs.setdefault(concrete_model, {})
            concrete_model_objs[concrete_model].setdefault(model, [])
            concrete_model_objs[concrete_model][model].append(obj)

        for concrete_model, model_objs in six.iteritems(concrete_model_objs):
            for model, objs in six.iteritems(model_objs):
                self.field_updates.setdefault(
                    model, {}
                ).setdefault(
                    (field, value), set()
                ).update(objs)

    def collect(self, objs, source=None, nullable=False, collect_related=True,
                source_attr=None, reverse_dependency=False):
        """
        Adds 'objs' to the collection of objects to be deleted as well as all
        parent instances.  'objs' must be a homogeneous iterable collection of
        model instances (e.g. a QuerySet).  If 'collect_related' is True,
        related objects will be handled by their respective on_delete handler.

        If the call is the result of a cascade, 'source' should be the model
        that caused it and 'nullable' should be set to True, if the relation
        can be null.

        If 'reverse_dependency' is True, 'source' will be deleted before the
        current model, rather than after. (Needed for cascading to parent
        models, the one case in which the cascade follows the forwards
        direction of an FK rather than the reverse direction.)
        """
        if self.can_fast_delete(objs):
            self.fast_deletes.append(objs)
            return
        new_objs = self.add(objs, source, nullable,
                            reverse_dependency=reverse_dependency)
        if not new_objs:
            return

        concrete_model_objs = {}
        for obj in new_objs:
            model = obj.__class__
            concrete_model = model._meta.concrete_model
            concrete_model_objs.setdefault(concrete_model, {})
            concrete_model_objs[concrete_model].setdefault(model, [])
            concrete_model_objs[concrete_model][model].append(obj)

        for concrete_model, model_objs in six.iteritems(concrete_model_objs):
            parent_objs = []
            for model, new_objs in six.iteritems(model_objs):
                # Recursively collect concrete model's parent models, but not their
                # related objects. These will be found by meta.get_all_related_objects()
                for ptr in six.itervalues(concrete_model._meta.parents):
                    if ptr:
                        # FIXME: This seems to be buggy and execute a query for each
                        # parent object fetch. We have the parent data in the obj,
                        # but we don't have a nice way to turn that data into parent
                        # object instance.
                        parent_objs += [getattr(obj, ptr.name) for obj in new_objs]
            if parent_objs:
                self.collect(parent_objs, source=model,
                             source_attr=ptr.rel.related_name,
                             collect_related=False,
                             reverse_dependency=True)

            if collect_related:
                for model, new_objs in six.iteritems(model_objs):
                    for related in deletion.get_candidate_relations_to_delete(model._meta):
                        field = related.field
                        if field.rel.on_delete == deletion.DO_NOTHING:
                            continue
                        batches = self.get_del_batches(new_objs, field)
                        for batch in batches:
                            sub_objs = self.related_objects(related, batch)
                            if self.can_fast_delete(sub_objs, from_field=field):
                                self.fast_deletes.append(sub_objs)
                            elif sub_objs:
                                field.rel.on_delete(self, field, sub_objs, self.using)
                    for field in model._meta.virtual_fields:
                        if hasattr(field, 'bulk_related_objects'):
                            # Its something like generic foreign key.
                            sub_objs = field.bulk_related_objects(new_objs, self.using)
                            self.collect(sub_objs,
                                         source=model,
                                         source_attr=field.rel.related_name,
                                         nullable=True)


# Monkey-patch the collector class.
for method_name in ('add', 'add_field_update', 'collect'):
    setattr(
        deletion.Collector,
        method_name,
        types.MethodType(
            getattr(PolymorphicCollector, method_name).im_func,
            None,
            deletion.Collector
        )
    )
