import copy
import hashlib
import os

from django import forms as django_forms, template
from django.db import transaction, models
from django.utils import datastructures

from ....utils import loader, toposort

from . import formstate
from .. import registration

__all__ = (
    'RegistryValidationError',
    'prepare_root_forms',
    'FORM_INITIAL',
    'FORM_OUTPUT',
    'FORM_DEFAULTS',
    'FORM_ONLY_DEFAULTS',
    'FORM_ROOT_CREATE',
    'FORM_SET_DEFAULTS',
    'FORM_DEFAULTS_ENABLED',
)


# Form generation flags.
FORM_INITIAL = 0x01
FORM_OUTPUT = 0x02
FORM_DEFAULTS = 0x04
FORM_ONLY_DEFAULTS = 0x08
FORM_ROOT_CREATE = 0x10
FORM_SET_DEFAULTS = 0x20
FORM_DEFAULTS_ENABLED = 0x40


class RegistryValidationError(Exception):
    """
    This exception can be raised by registry point validation hooks to
    notify the API that validation has failed.
    """

    pass


class BasicRegistryRenderItem(object):
    """
    A simple registry render item that includes a form with fields and
    an item class selector when needed.
    """

    template = 'registry/basic_render_item.html'

    def __init__(self, form, meta_form, **kwargs):
        """
        Class constructor.

        :param form: Form containing the fields
        :param meta_form: Form containing selected item metadata
        """

        self.form = form
        self.meta_form = meta_form
        self.args = kwargs

    @property
    def media(self):
        """
        Returns the form Media object for this render item.
        """

        if self.form is not None and self.meta_form is not None:
            return self.form.media + self.meta_form.media
        else:
            return None

    def __unicode__(self):
        """
        Renders this item.
        """

        t = template.loader.get_template(self.template)
        args = {
            'form': self.form,
            'meta': self.meta_form,
        }
        args.update(self.args)
        return t.render(template.Context(args))


class NestedRegistryRenderItem(BasicRegistryRenderItem):
    """
    A registry renderer item that augments the basic form with support for
    nested forms.
    """

    template = 'registry/nested_render_item.html'

    def __init__(self, form, meta_form, children, **kwargs):
        """
        Class constructor.

        :param form: Form containing the fields
        :param meta_form: Form containing selected item metadata
        :param children: A list of child form descriptors
        """

        super(NestedRegistryRenderItem, self).__init__(form, meta_form, registry_forms=children, **kwargs)
        self.children = children

    @property
    def media(self):
        """
        Returns the form Media object for this render item.
        """

        base_media = super(NestedRegistryRenderItem, self).media

        for child in self.children:
            # Include media from all child render items
            for subform in child['subforms']:
                if base_media is not None:
                    base_media += subform.media
                else:
                    base_media = subform.media

            # Include media from meta form
            if child['submeta'] is not None:
                base_media += child['submeta'].media

        return base_media


class RootRegistryRenderItem(NestedRegistryRenderItem):
    """
    A registry render item that is returned as the root of the render
    tree. It contains and renders all top-level forms.
    """

    template = 'registry/render_items.html'

    def __init__(self, context, forms):
        """
        Class constructor.

        :param context: Registry form render context
        :param forms: A list of form descriptors
        """

        super(RootRegistryRenderItem, self).__init__(None, None, forms)
        self.errors = []
        self.regpoint = context.regpoint.name
        self.root = context.root.pk if context.root else None
        self.form_id = context.form_id
        self.form_state = context.form_state

    def add_error(self, message):
        """
        Adds a global error message to be displayed.

        :param message: Message string
        """

        self.errors.append(message)

    def __unicode__(self):
        """
        Renders this item.
        """

        t = template.loader.get_template(self.template)
        args = {
            'registry_forms': self.children,
            'errors': self.errors,
        }
        return t.render(template.Context(args))


class RegistryMetaForm(django_forms.Form):
    """
    Form for selecting which item should be displayed.
    """

    def __init__(self, context, selected_item=None, force_selector_widget=False, static=False, instance_mid=0, *args, **kwargs):
        """
        Class constructor.
        """

        super(RegistryMetaForm, self).__init__(*args, **kwargs)

        # Choose a default item in case one is not set
        if selected_item is None:
            selected_item = context.items.values()[0]
        selected_item = selected_item._meta.model_name

        if not static and (len(context.items) > 1 or force_selector_widget):
            item_widget = django_forms.Select(attrs={'class': 'registry_form_item_chooser'})
        else:
            item_widget = django_forms.HiddenInput

        # Generate list of item choices
        item_choices = [(name, item.RegistryMeta.registry_name) for name, item in context.items.iteritems()]

        self.fields['item'] = django_forms.TypedChoiceField(
            choices=item_choices,
            coerce=str,
            initial=selected_item,
            widget=item_widget,
        )
        self.fields['prev_item'] = django_forms.TypedChoiceField(
            choices=item_choices,
            coerce=str,
            initial=selected_item,
            widget=django_forms.HiddenInput,
        )

        # Existing model identifier
        self.fields['mid'] = django_forms.IntegerField(
            initial=instance_mid,
            widget=django_forms.HiddenInput,
        )


class RegistrySetMetaForm(django_forms.Form):
    form_count = django_forms.IntegerField(
        min_value=0,
        max_value=10,
        widget=django_forms.HiddenInput,
    )


def generate_form_for_class(context, prefix, data, index, instance=None,
                            force_selector_widget=False, static=False):
    """
    A helper function for generating a form for a specific registry item class.
    """

    selected_item = instance.__class__ if instance is not None else None
    previous_item = None
    existing_mid = (instance.pk if instance is not None else 0) or 0

    # Parse a form that holds the item selector
    meta_form = RegistryMetaForm(
        context, selected_item, data=data,
        prefix=context.get_prefix(prefix),
        force_selector_widget=force_selector_widget,
        static=static, instance_mid=existing_mid,
    )
    if not (context.flags & FORM_INITIAL) and not static:
        if not meta_form.is_valid():
            context.validation_errors = True
        else:
            selected_item = context.items.get(meta_form.cleaned_data['item'])
            previous_item = context.items.get(meta_form.cleaned_data['prev_item'])
            existing_mid = meta_form.cleaned_data['mid']

    # Fallback to default item in case of severe problems (this should not happen in normal
    # operation, but might happen when someone tampers with the form)
    if selected_item is None:
        selected_item = context.items.values()[0]

    # Items have changed between submissions, we should copy some field values from the
    # previous form to the new one
    if previous_item is not None and selected_item != previous_item and not static:
        pform = previous_item.get_form()(
            data,
            prefix=context.get_prefix(prefix, previous_item),
        )

        # Perform a partial clean and copy all valid fields to the new form
        pform.cleaned_data = {}
        pform._errors = {}
        pform._clean_fields()
        for field in pform.cleaned_data.keys():
            prev_item_field = context.get_prefix(prefix, previous_item, field)
            if prev_item_field in data:
                data[context.get_prefix(prefix, selected_item, field)] = data[prev_item_field]

    # When there is no instance, we should create one so we will be able to save somewhere
    if not (context.flags & FORM_INITIAL) and context.flags & FORM_OUTPUT and instance is None:
        # Check if we can reuse an existing instance
        existing_instance = context.existing_models.get(existing_mid, None)
        if isinstance(existing_instance, selected_item):
            instance = existing_instance
            instance._skip_delete = True
        else:
            instance = selected_item(root=context.root)

    # Populate data with default values from the registry item instance
    if selected_item != previous_item and instance is not None:
        model_data = django_forms.model_to_dict(instance)
        for field_name, values in model_data.iteritems():
            field_name_prefix = context.get_prefix(prefix, selected_item, field_name)
            if data is not None and field_name_prefix not in data:
                context.data_from_field(prefix, selected_item, field_name, values, data)

    # Ensure that the instance root is properly set.
    if instance is not None:
        instance.root = context.root

    # Now generate a form for the selected item
    form_prefix = context.get_prefix(prefix, selected_item)
    form = selected_item.get_form()(
        data,
        instance=instance,
        prefix=form_prefix,
    )

    # Fetch the current item in form state representation.
    form_modified = False
    form_attributes = {}
    if context.flags & FORM_OUTPUT:
        state_item = context.form_state.lookup_item(selected_item, index, context.hierarchy_parent_current)
        if state_item is not None:
            form_attributes['index'] = state_item._id

        def modify_to_context(obj):
            if not hasattr(obj, 'modify_to_context'):
                return False

            obj.modify_to_context(state_item, context.form_state, context.request)
            return True

        # Enable forms to modify themselves accoording to current context
        form_modified = modify_to_context(form)

        # Enable form fields to modify themselves accoording to current context
        for name, field in form.fields.iteritems():
            if modify_to_context(field):
                form_modified = True
    else:
        state_item = None

    config = None
    if not (context.flags & FORM_INITIAL):
        if context.flags & FORM_OUTPUT:
            # Perform a full validation and save the form
            if form.is_valid():
                form_id = (instance.get_registry_id(), id(context.hierarchy_parent_obj), index)
                assert form_id not in context.pending_save_forms

                # Setup dependencies among forms
                dependencies = set()
                for name, field in form.fields.iteritems():
                    if hasattr(field, 'get_dependencies'):
                        dependencies.update(field.get_dependencies(form.cleaned_data.get(name, None)))

                # If we have a parent, we depend on it
                if context.hierarchy_parent_obj is not None:
                    parent_id = (
                        context.hierarchy_parent_obj.get_registry_id(),
                        id(context.hierarchy_grandparent_obj),
                        context.hierarchy_parent_index,
                    )
                    dependencies.add(parent_id)
                    context.pending_save_foreign_keys.setdefault(parent_id, []).append(
                        (form_id, selected_item._registry_object_parent_link.name)
                    )

                # Add form to list of forms pending save together with dependencies
                context.pending_save_forms[form_id] = {
                    'registry_id': instance.get_registry_id(),
                    'index': index,
                    'form': form,
                    'form_id': form_id,
                    'dependencies': dependencies,
                }
            else:
                context.validation_errors = True

            # Update the current config item as it may have changed due to modify_to_context calls.
            if form_modified and state_item is not None:
                pform = copy.copy(form)
                pform.cleaned_data = {}
                pform._errors = {}
                pform._clean_fields()

                for field in state_item._meta.fields:
                    if not field.editable or field.rel is not None:
                        continue

                    try:
                        setattr(state_item, field.name, pform.cleaned_data.get(field.name, None))
                    except AttributeError:
                        pass
        else:
            # We are only interested in all the current values even if they might be incomplete
            # and/or invalid, so we can't do full form validation.
            form.cleaned_data = {}
            form._errors = {}
            form._clean_fields()
            config = context.form_state.create_item(selected_item, form.cleaned_data, context.hierarchy_parent_partial, index)

    # Generate a new meta form, since the previous item has now changed
    meta_form = RegistryMetaForm(
        context, selected_item,
        prefix=context.get_prefix(prefix),
        force_selector_widget=force_selector_widget,
        static=static, instance_mid=existing_mid,
    )

    # Pack forms into a proper abstract representation
    if selected_item.has_registry_children():
        sub_context = RegistryFormContext(
            regpoint=context.regpoint,
            request=context.request,
            root=context.root,
            data=context.data,
            save=context.save,
            hierarchy_prefix=form_prefix,
            hierarchy_parent_cls=selected_item,
            hierarchy_parent_obj=instance,
            hierarchy_parent_partial=config,
            hierarchy_parent_current=state_item,
            hierarchy_parent_index=index,
            hierarchy_grandparent_obj=context.hierarchy_parent_obj,
            validation_errors=False,
            pending_save_forms=context.pending_save_forms,
            pending_save_foreign_keys=context.pending_save_foreign_keys,

            form_state=context.form_state,
            flags=context.flags,
        )

        forms = NestedRegistryRenderItem(form, meta_form, prepare_forms(sub_context), **form_attributes)

        # Validation errors flag must propagate upwards
        if sub_context.validation_errors:
            context.validation_errors = True
    else:
        forms = BasicRegistryRenderItem(form, meta_form, **form_attributes)

    return forms


class RegistryFormContext(object):
    """
    Form render context.
    """
    regpoint = None
    request = None
    root = None
    data = None
    save = False

    form_state = None
    flags = 0

    validation_errors = False
    subforms = None
    hierarchy_parent_cls = None
    hierarchy_parent_obj = None
    hierarchy_parent_partial = None
    hierarchy_parent_current = None
    hierarchy_parent_index = None
    hierarchy_grandparent_obj = None
    hierarchy_prefix = None
    base_prefix = None
    default_item_cls = None
    force_selector_widget = False
    items = None
    existing_items = None
    existing_models = None
    pending_save_forms = None
    pending_save_foreign_keys = None

    def __init__(self, **kwargs):
        """
        Class constructor.
        """
        self.__dict__.update(kwargs)
        self._form_id = None

        if self.form_id not in self.request.session:
            self.state = {}

    def get_prefix(self, prefix, item=None, field=None):
        """
        Returns a formatted form prefix, optionally together with a field id.
        """

        if item is None:
            form_prefix = prefix
        else:
            form_prefix = '%s_%s' % (prefix, item._meta.model_name)

        if field is None:
            return form_prefix
        else:
            return '%s-%s' % (form_prefix, field)

    def data_from_field(self, prefix, item, field, value, data=None):
        if data is None:
            data = self.data

        if not isinstance(value, (list, tuple)):
            # We need to support updates of lists of values.
            value = [value]

        field_name = self.get_prefix(prefix, item, field)
        for scalar_value in value:
            data.update({field_name: scalar_value})

    @property
    def form_id(self):
        """
        Returns the unique form identifier. If one is not yet configured,
        a new one is generated.
        """

        if not self._form_id:
            if not self.data or 'registry_form_id' not in self.data:
                self._form_id = hashlib.sha1('registry-form-%s' % os.urandom(32)).hexdigest()
            else:
                self._form_id = self.data['registry_form_id']

        return self._form_id

    def _get_state(self):
        """
        Rule evaluation state getter.
        """

        self.request.session.modified = True
        return self.request.session[self.form_id]

    def _set_state(self, value):
        """
        Rule evaluation state setter.
        """

        self.request.session[self.form_id] = value
        self.request.session.modified = True

    state = property(_get_state, _set_state)

    def clear_state(self):
        """
        Clears rule evaluation state.
        """

        del self.request.session[self.form_id]
        self.request.session.modified = True


def prepare_forms(context):
    """
    Prepares forms for some registry items.
    """

    forms = []
    for items in context.regpoint.get_children(context.hierarchy_parent_cls):
        # TODO: Is a deep copy really needed? Shouldn't a shallow one suffice?
        context.items = copy.deepcopy(items)
        context.existing_items = set()

        # Discover which class is the top-level class
        if context.hierarchy_parent_cls is not None:
            for item_cls in context.items.values():
                if all([issubclass(x, item_cls) for x in context.items.values()]):
                    break
            else:
                item_cls = context.items.values()[0].get_registry_toplevel()
        else:
            item_cls = context.items.values()[0].get_registry_toplevel()
        cls_meta = item_cls.RegistryMeta

        if context.hierarchy_prefix is not None:
            context.base_prefix = context.hierarchy_prefix + '_' + cls_meta.registry_id.replace('.', '_')
        else:
            context.base_prefix = 'reg_' + cls_meta.registry_id.replace('.', '_')

        context.subforms = []
        context.force_selector_widget = False

        if getattr(cls_meta, 'hidden', False) and item_cls._meta.model_name in context.items:
            # The top-level item should be hidden
            del context.items[item_cls._meta.model_name]
            context.force_selector_widget = True

            # When there is only the top-level item and it should be hidden, we don't
            # render this whole item class section
            if not context.items:
                continue

        # Fetch existing models for this item
        context.existing_models = datastructures.SortedDict()
        if context.root is not None:
            existing_models_qs = context.regpoint.get_accessor(context.root).by_registry_id(cls_meta.registry_id, queryset=True)

            if context.hierarchy_parent_cls is not None:
                rel_field_name = item_cls._registry_object_parent_link.name
                if item_cls != item_cls.get_registry_toplevel():
                    rel_field_name = "%s__%s" % (item_cls._meta.model_name, rel_field_name)
                    # We have to filter out completely unrelated items because if the parent object
                    # is set to None, the basic filter would also match those that aren't linked
                    # to the correct model at all.
                    existing_models_qs = existing_models_qs.exclude(
                        **{item_cls._meta.model_name: None}
                    )

                existing_models_qs = existing_models_qs.filter(
                    **{rel_field_name: context.hierarchy_parent_obj}
                )

            for mdl in existing_models_qs:
                mdl = mdl.cast()

                # When we are looking for existing top-level objects in object hierarchy, we should
                # skip those that have the parent link set to a non-NULL value
                if context.hierarchy_parent_cls is None and \
                   getattr(mdl, '_registry_object_parent', None) is not None:
                    if getattr(mdl, mdl._registry_object_parent_link.name) is not None:
                        continue

                # Skip items that should not be here
                if mdl._meta.model_name not in context.items:
                    continue

                context.existing_models[mdl.pk] = mdl
                context.existing_items.add(mdl.__class__)

        # Remove all items that should not be visible
        for key, value in context.items.items():
            if value._registry_hide_requests > 0:
                del context.items[key]
                continue

            # TODO: Reimplement permissions checks. Be careful on interaction with FormState.

        if not context.items:
            continue

        context.default_item_cls = context.items.values()[0]

        if getattr(cls_meta, 'multiple', False):
            # This is an item class that supports multiple objects of the same class
            if getattr(cls_meta, 'multiple_static', False):
                # All multiple objects that are registered should always be displayed
                for index, item in enumerate(context.items.values()):
                    mdl = None
                    for emdl in context.existing_models.values():
                        if isinstance(emdl, item):
                            mdl = emdl
                            break
                    else:
                        if context.root is not None:
                            mdl = item(root=context.root)
                        else:
                            mdl = item()

                    form_prefix = context.base_prefix + '_mu_' + str(index)
                    context.subforms.append(generate_form_for_class(
                        context,
                        form_prefix,
                        context.data,
                        index,
                        instance=mdl,
                        static=True,
                    ))
            else:
                # Dynamically modifiable multiple objects
                if not context.save and not context.flags & FORM_ONLY_DEFAULTS:
                    # We are generating forms for first-time display purpuses, only include forms for
                    # existing models
                    for index, mdl in enumerate(context.existing_models.values()):
                        form_prefix = context.base_prefix + '_mu_' + str(index)
                        context.subforms.append(generate_form_for_class(
                            context,
                            form_prefix,
                            None,
                            index,
                            instance=mdl,
                            force_selector_widget=context.force_selector_widget,
                        ))

                    # Create the form that contains metadata for this formset
                    submeta = RegistrySetMetaForm(
                        context.data,
                        prefix=context.get_prefix(context.base_prefix + '_sm'),
                        initial={'form_count': len(context.subforms)},
                    )
                else:
                    # We are saving or preparing to evaluate rules
                    submeta = RegistrySetMetaForm(
                        context.data,
                        prefix=context.get_prefix(context.base_prefix + '_sm'),
                    )
                    form_count = 0
                    if submeta.is_valid():
                        form_count = submeta.cleaned_data['form_count']
                    else:
                        submeta = RegistrySetMetaForm(
                            prefix=context.get_prefix(context.base_prefix + '_sm'),
                            initial={'form_count': 0},
                        )

                    # Setup the expected number of forms if only user-supplied forms are counted;
                    # this might not be correct when rules have changed the partial configuration.
                    context.user_form_count = form_count
                    meta_modified = False

                    # Execute before actions.
                    for action in context.form_state.get_form_actions(cls_meta.registry_id):
                        if action.modify_forms_before(context):
                            meta_modified = True

                    # Actions might have changed form count.
                    form_count = context.user_form_count

                    # Generate the right amount of forms.
                    for index in xrange(form_count):
                        # Generate form prefix.
                        form_prefix = context.base_prefix + '_mu_' + str(index)

                        updated_form = None
                        for action in context.form_state.get_form_actions(cls_meta.registry_id):
                            form = action.modify_form(context, index, form_prefix)
                            if form is not None:
                                updated_form = form

                        if updated_form:
                            # In case an action generates the form for us, we can just use it instead
                            # of generating the default form.
                            context.subforms.append(updated_form)
                        else:
                            # Otherwise, we generate a default form.
                            context.subforms.append(generate_form_for_class(
                                context,
                                form_prefix,
                                context.data,
                                index,
                                force_selector_widget=context.force_selector_widget,
                            ))

                    # Delete existing models
                    for mdl in context.existing_models.values():
                        if not getattr(mdl, '_skip_delete', False):
                            mdl.delete()

                    # Check for any actions and execute them.
                    for action in context.form_state.get_form_actions(cls_meta.registry_id):
                        if action.modify_forms_after(context):
                            meta_modified = True

                    if meta_modified:
                        # Update the submeta form with new count.
                        submeta = RegistrySetMetaForm(
                            prefix=context.get_prefix(context.base_prefix + '_sm'),
                            initial={'form_count': len(context.subforms)},
                        )
        else:
            # This item class only supports a single object to be selected
            try:
                mdl = context.existing_models.values()[0]

                if context.save or context.flags & FORM_ONLY_DEFAULTS:
                    mdl = None
            except IndexError:
                mdl = None

            assert not context.subforms
            form_prefix = context.base_prefix + '_mu_0'

            # Execute form actions.
            for action in context.form_state.get_form_actions(cls_meta.registry_id):
                action.modify_forms_before(context)
                action.modify_form(context, 0, form_prefix)
                action.modify_forms_after(context)

            assert len(context.subforms) <= 1

            if not context.subforms:
                context.subforms.append(generate_form_for_class(
                    context,
                    form_prefix,
                    context.data,
                    0,
                    instance=mdl,
                ))

            submeta = None

        forms.append({
            'name': cls_meta.registry_section,
            'id': cls_meta.registry_id,
            'multiple': getattr(cls_meta, 'multiple', False),
            'hide_multiple_controls': getattr(cls_meta, 'multiple_static', False),
            'subforms': context.subforms,
            'submeta': submeta,
            'prefix': context.base_prefix,
            'parent_id': context.hierarchy_parent_current._id if context.hierarchy_parent_current else '',
        })

    return forms


@transaction.atomic(savepoint=False)
def prepare_root_forms(regpoint, request, root=None, data=None, save=False, form_state=None, flags=0):
    """
    Prepares a list of configuration forms for use on a regpoint root's
    configuration page.

    :param regpoint: Registration point name or instance
    :param request: Request instance
    :param root: Registration point root instance for which to generate forms
    :param data: User-supplied POST data
    :param save: Are we performing a save or rendering an initial form
    """

    # Ensure that all registry forms, form processors and CGMs are registered.
    loader.load_modules('forms', 'formprocessors', 'cgm')

    if save and flags & FORM_ONLY_DEFAULTS:
        raise ValueError("You cannot use save and FORM_ONLY_DEFAULTS at the same time!")

    if isinstance(regpoint, basestring):
        regpoint = registration.point(regpoint)

    # Transform data into a mutable dictionary in case an immutable one is passed
    data = copy.copy(data)

    # Prepare context
    context = RegistryFormContext(
        regpoint=regpoint,
        request=request,
        root=root,
        data=data,
        save=save,
        validation_errors=False,
        pending_save_forms={},
        pending_save_foreign_keys={},
        form_state=form_state if form_state is not None else formstate.FormState(regpoint),
        flags=flags,
    )

    # Load initial form state when requested and available.
    if flags & FORM_INITIAL and root is not None:
        context.form_state = formstate.FormState.from_db(regpoint, root)
        context.state = {
            'metadata': regpoint.get_root_metadata(root)
        }
    elif not context.state:
        context.state = {
            'metadata': {},
        }

    context.form_state.set_metadata(context.state['metadata'])
    if flags & FORM_SET_DEFAULTS:
        context.form_state.set_using_defaults(flags & FORM_DEFAULTS_ENABLED)

    # Prepare form processors.
    form_processors = []
    for form_processor in regpoint.get_form_processors():
        form_processor = form_processor()
        form_processor.preprocess(root)
        form_processors.append(form_processor)

    try:
        sid = transaction.savepoint()
        forms = RootRegistryRenderItem(context, prepare_forms(context))

        if flags & FORM_DEFAULTS | FORM_ONLY_DEFAULTS:
            # Set form defaults.
            context.form_state.apply_form_defaults(regpoint, flags & FORM_ROOT_CREATE)

            if flags & FORM_ONLY_DEFAULTS:
                # If only defaults application is requested, we should set defaults and then rollback
                # the savepoint in any case; all validation errors are ignored.
                transaction.savepoint_rollback(sid)
                return context.form_state

        # Process forms when saving and there are no validation errors
        if save and root is not None and not context.validation_errors:
            # Resolve form dependencies and save all forms
            for layer, linear_forms in enumerate(toposort.topological_sort(context.pending_save_forms)):
                for info in linear_forms:
                    form = info['form']

                    # Before saving the form perform the validation again so dependent
                    # fields can be recalculated
                    form._clean_fields()
                    form._clean_form()
                    form._post_clean()

                    if form.is_valid():
                        # Save the form and store the instance into partial configuration so
                        # dependent objects can reference the new instance
                        instance = form.save()
                        # Only overwrite instances at the top layer (forms which have no dependencies
                        # on anything else). Models with dependencies will already be updated when
                        # calling save.
                        if layer == 0 and info['registry_id'] in context.form_state:
                            context.form_state[info['registry_id']][info['index']] = instance

                        for form_id, field in context.pending_save_foreign_keys.get(info['form_id'], []):
                            setattr(
                                context.pending_save_forms[form_id]['form'].instance,
                                field,
                                instance
                            )
                    else:
                        context.validation_errors = True

            # Execute any validation hooks.
            for processor in form_processors:
                try:
                    processor.postprocess(root)
                except RegistryValidationError, e:
                    context.validation_errors = True
                    forms.add_error(e.message)

        if not context.validation_errors:
            # Persist metadata.
            regpoint.set_root_metadata(root, context.state['metadata'])
            root.save()

            transaction.savepoint_commit(sid)
            context.clear_state()
        else:
            transaction.savepoint_rollback(sid)
    except RegistryValidationError:
        transaction.savepoint_rollback(sid)
    except transaction.TransactionManagementError:
        raise
    except:
        transaction.savepoint_rollback(sid)
        raise

    return forms if not save else (context.validation_errors, forms)
