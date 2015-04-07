from . import base

__all__ = (
    'RemoveFormAction',
    'AppendFormAction',
    'AssignToFormAction',
)


class RegistryFormAction(object):
    """
    An abstract action that can modify lists of registry forms.
    """

    context = None

    def modify_forms_before(self):
        """
        Subclasses should provide action implementation in this method. It
        will be executed before the subforms are generated.
        """

        pass

    def modify_forms_after(self):
        """
        Subclasses should provide action implementation in this method. It
        will be executed after the subforms are generated.
        """

        pass


class RemoveFormAction(RegistryFormAction):
    """
    An action that removes forms specified by index.
    """

    def __init__(self, indices, parent=None):
        """
        Class constructor.

        :param indices: Form indices to remove
        :param parent: Optional partial parent item
        """

        self.indices = sorted(indices)
        self.parent = parent

    def modify_forms_before(self):
        """
        Removes specified subforms.
        """

        if self.parent != self.context.hierarchy_parent_current or len(self.indices) < 1:
            return False

        # Move form data as forms might be renumbered
        form_prefix = self.context.base_prefix + '_mu_'
        reduce_by = 0
        for i in xrange(self.context.user_form_count):
            if i in self.indices:
                for key in self.context.data.keys():
                    if key.startswith(form_prefix + str(i) + '_') or key.startswith(form_prefix + str(i) + '-'):
                        del self.context.data[key]

                reduce_by += 1
                continue
            elif not reduce_by:
                continue

            for key in self.context.data.keys():
                postfix = None
                if key.startswith(form_prefix + str(i) + '_'):
                    postfix = '_'
                elif key.startswith(form_prefix + str(i) + '-'):
                    postfix = '-'

                if postfix is not None:
                    new_key = key.replace(form_prefix + str(i) + postfix, form_prefix + str(i - reduce_by) + postfix)
                    self.context.data[new_key] = self.context.data[key]
                    del self.context.data[key]

        # Reduce form count depending on how many forms have been removed
        self.context.user_form_count -= len(self.indices)
        return True


class AppendFormAction(RegistryFormAction):
    """
    An action that appends a new form at the end of current subforms.
    """

    def __init__(self, item, parent=None):
        """
        Class constructor.

        :param item: Configuration item that should be appended
        :param parent: Optional partial parent item
        """

        self.item = item
        self.parent = parent

    def modify_forms_after(self):
        """
        Appends a new form at the end of current subforms.
        """

        if self.parent != self.context.hierarchy_parent_current:
            return False

        form_prefix = self.context.base_prefix + '_mu_' + str(len(self.context.subforms))
        item = self.item
        if item is None:
            item = self.context.form_state.create_item(
                self.context.default_item_cls,
                {},
                parent=self.context.hierarchy_parent_current,
            )

        self.context.subforms.append(base.generate_form_for_class(
            self.context,
            form_prefix,
            None,
            len(self.context.subforms),
            instance=item,
            force_selector_widget=self.context.force_selector_widget,
        ))

        return True


class AssignToFormAction(RegistryFormAction):
    """
    An action that assigns to an existing form.
    """

    def __init__(self, item, index, attributes, parent=None):
        """
        Class constructor.

        :param item: Configuration item
        :param index: Subform index
        :param attributes: A dictionary of attributes to assign
        :param parent: Optional partial parent item
        """

        self.item = item
        self.index = index
        self.attributes = attributes
        self.parent = parent

    def modify_forms_before(self):
        """
        Assigns to an existing form.
        """

        if self.parent != self.context.hierarchy_parent_current:
            return False

        form_prefix = self.context.base_prefix + '_mu_' + str(self.index)
        for field, value in self.attributes.items():
            self.context.data[form_prefix + '_' + self.item._meta.model_name + '-' + field] = value

        return True
