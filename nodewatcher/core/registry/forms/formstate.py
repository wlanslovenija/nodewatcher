import hashlib
import itertools

from django.core import exceptions


class FormState(dict):
    def __init__(self, registration_point):
        """
        Class constructor.

        :param registration_point: Registration point instance
        """

        self.registration_point = registration_point
        self._form_actions = {}
        self._item_map = {}

    def get_form_actions(self, registry_id):
        """
        Returns all the pending form actions.

        :param registry_id: Registry identifier to return the actions for
        """

        return self._form_actions.get(registry_id, [])

    def add_form_action(self, registry_id, action):
        """
        Adds a new form action to the pending actions list.

        :param registry_id: Registry identifier this action should execute for
        :param action: Action instance
        """

        self._form_actions.setdefault(registry_id, []).append(action)

    def filter_items(self, registry_id, item_id=None, klass=None, parent=None, **kwargs):
        """
        Filters form state items based on specified criteria.

        :param registry_id: Registry identifier
        :param item_id: Optional item identifier filter
        :param klass: Optional item class filter
        :param parent: Optional parent instance filter
        :return: A list of form state items
        """

        items = []

        # Validate that the specified registry identifier is actually correct.
        self.registration_point.get_top_level_class(registry_id)

        # When an item identifier is passed in, we can get the item directly.
        if item_id is not None:
            items.append(self.lookup_item_by_id(item_id))
        else:
            # Resolve parent item when specified as a filter expression.
            if isinstance(parent, basestring):
                parent = self.lookup_item_by_id(parent)
                if parent is None:
                    raise ValueError("Parent item cannot be found.")
            elif parent is not None and not hasattr(parent, '_registry_virtual_relation'):
                raise TypeError("Parent must be either an item instance or an item identifier.")

            if parent is not None:
                items_container = itertools.chain(*parent._registry_virtual_relation.values())
            else:
                items_container = self.get(registry_id, [])

            for item in items_container:
                # Filter based on specified class.
                if klass is not None and item.__class__ != klass:
                    continue

                # Filter based on partial values.
                if kwargs:
                    match = True
                    for key, value in kwargs.iteritems():
                        if not key.startswith('_') and getattr(item, key, None) != value:
                            match = False
                            break

                    if not match:
                        continue

                items.append(item)

        return items

    def remove_items(self, registry_id, **kwargs):
        """
        Removes items specified by a filter expression. Arguments should be the
        same as to `filter_items` method.
        """

        from . import actions

        # Chack that the specified registry item can be removed.
        item_class = self.registration_point.get_top_level_class(registry_id)
        if not item_class.has_registry_multiple():
            raise ValueError("Attempted to remove a singular registry item '%s'!" % registry_id)
        if item_class.is_registry_multiple_static():
            raise ValueError("Attempted to remove a static registry item '%s'!" % registry_id)

        # Run a filter to get the items.
        for item in self.filter_items(registry_id, **kwargs):
            container = item._registry_virtual_parent_items_container
            container.remove(item)

            # Add form actions to remove form data.
            self.add_form_action(
                registry_id,
                actions.RemoveFormAction(
                    [item._registry_virtual_child_index],
                    parent=item.get_registry_parent(),
                )
            )

            # Update indices and identifiers of other items in the same container.
            for sibling in container:
                sibling._registry_virtual_child_index = container.index(sibling)
                del self._item_map[sibling._id]
                sibling._id = self.get_identifier(sibling)
                self._item_map[sibling._id] = sibling

    def remove_item(self, identifier_or_item):
        """
        Removes a form state item.

        :param identifier_or_item: Item identifier or instance
        """

        if hasattr(identifier_or_item, '_id'):
            item = identifier_or_item
        else:
            item = self.lookup_item_by_id(identifier_or_item)

        self.remove_items(item.get_registry_id(), _id=item._id)

    def update_item(self, identifier_or_item, **attributes):
        """
        Updates a form state item's attributes.

        :param identifier_or_item: Item identifier or instance
        """

        from . import actions

        if hasattr(identifier_or_item, '_id'):
            item = identifier_or_item
        else:
            item = self.lookup_item_by_id(identifier_or_item)

        # Update item attributes.
        modified = {}
        for key, value in attributes.items():
            if getattr(item, key, None) != value:
                setattr(item, key, value)
                modified[key] = value

        if modified:
            # Add form action to modify data.
            self.add_form_action(
                item.get_registry_id(),
                actions.AssignToFormAction(
                    item,
                    item._registry_virtual_child_index,
                    modified,
                    parent=item.get_registry_parent(),
                )
            )

    def append_default_item(self, registry_id, parent_identifier=None):
        """
        Appends a default item to a specified part of form state.

        :param registry_id: Registry identifier of the appended item
        :param parent_identifier: Optional identifier of the parent object
        """

        from . import actions

        # Validate that the specified registry identifier is actually correct.
        self.registration_point.get_top_level_class(registry_id)

        parent = self.lookup_item_by_id(parent_identifier) if parent_identifier else None
        self.add_form_action(registry_id, actions.AppendFormAction(None, parent))

    def get_identifier(self, item):
        """
        Returns an encoded identifier for a form state item.

        :param item: Form state item
        """

        identifier = []
        if item.has_registry_parent():
            identifier.append(self.get_identifier(item.get_registry_parent()))

        identifier += [
            item.get_registry_id(),
            item.__class__.__name__,
            item._registry_virtual_child_index
        ]

        return hashlib.sha1(".".join([str(atom) for atom in identifier])).hexdigest()

    def create_item(self, cls, attributes, parent=None, index=None):
        """
        Creates a new form state item.

        :param cls: Form state item class
        :param attributes: Attributes dictionary to set for the new item
        :param parent: Optional parent item
        :param index: Optional index to overwrite an existing item
        :return: Created form state item
        """

        item = cls()
        item._registry_virtual_model = True
        items_container = None
        if parent is not None:
            setattr(item, cls._registry_object_parent_link.name, parent)

            # Create a virtual reverse relation in the parent object.
            virtual_relation = getattr(parent, '_registry_virtual_relation', {})
            desc = getattr(parent.__class__, cls._registry_object_parent_link.rel.related_name)
            items_container = virtual_relation.setdefault(desc, [])
            parent._registry_virtual_relation = virtual_relation

            if index is not None:
                try:
                    virtual_relation[desc][index] = item
                except IndexError:
                    # If parent was replaced, this virtual relation might not exist, so
                    # we must create it again as normal. In this case, index must always
                    # be the same as the length of the list.
                    assert index == len(items_container)
                    items_container.append(item)
            else:
                index = len(items_container)
                items_container.append(item)
        elif index is not None:
            items_container = self.setdefault(cls.get_registry_id(), [])
            try:
                items_container[index] = item
            except IndexError:
                assert index == len(items_container)
                items_container.append(item)
        else:
            items_container = self.setdefault(cls.get_registry_id(), [])
            index = len(items_container)
            items_container.append(item)

        item._registry_virtual_parent_items_container = items_container
        item._registry_virtual_child_index = index
        item._id = self.get_identifier(item)
        self._item_map[item._id] = item

        for field, value in attributes.iteritems():
            try:
                setattr(item, field, value)
            except (exceptions.ValidationError, ValueError):
                pass

        return item

    def lookup_item(self, cls, index, parent=None):
        """
        Performs a form state item lookup.

        :param cls: Item class
        :param index: Item index
        :param parent: Optional item parent
        """

        try:
            if parent is not None:
                return getattr(parent, cls._registry_object_parent_link.rel.related_name)[index]
            else:
                return self[cls.get_registry_id()][index]
        except (KeyError, IndexError):
            return None

    def lookup_item_by_id(self, identifier):
        """
        Looks up an item by its identifier.

        :param identifier: Item identifier
        """

        return self._item_map.get(identifier, None)

    @classmethod
    def from_db(cls, registration_point, root):
        """
        Generates form state from current registry items stored in the database.

        :param registration_point: Registration point instance
        :param root: Root model instance
        :return: Instance of FormState populated from the database
        """

        form_state = FormState(registration_point)
        item_map = {}
        pending_children = []

        def convert_child_item(item, attributes):
            # Skip already converted items.
            if (item.__class__, item.pk) in item_map:
                return

            # Obtain the real parent (as set in the database).
            real_parent = getattr(item, item._registry_object_parent_link.name)
            # Check if there is already a mapping from real parent to converted parent.
            try:
                mapped_parent = item_map[(real_parent.__class__, real_parent.pk)]
            except KeyError:
                # No mapping exists yet, defer creation of this child item.
                pending_children.append((item, attributes))
                return

            item_map[(item.__class__, item.pk)] = form_state.create_item(item.__class__, attributes, mapped_parent)

        def convert_items(parent=None):
            for cls in registration_point.get_children(parent):
                toplevel_cls = cls.values()[0]

                for item in registration_point.get_accessor(root).by_registry_id(toplevel_cls.get_registry_id(), queryset=True):
                    # Skip already converted items.
                    if (item.__class__, item.pk) in item_map:
                        return

                    # Copy attributes from item.
                    attributes = {}
                    for field in item._meta.fields:
                        if not field.editable or field.primary_key:
                            continue

                        attributes[field.name] = getattr(item, field.name, None)

                    if item.has_registry_parent():
                        convert_child_item(item, attributes)
                    else:
                        item_map[(item.__class__, item.pk)] = form_state.create_item(item.__class__, attributes)

                # Convert also all subitems.
                for cls in cls.values():
                    if cls.has_registry_children():
                        convert_items(cls)

        # Start the conversion process with top-level registry items.
        convert_items()

        # Register all parent links as virtual relations.
        while pending_children:
            convert_child_item(*pending_children.pop())

        return form_state
