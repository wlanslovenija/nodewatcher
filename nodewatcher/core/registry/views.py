import json

from django import http, shortcuts, template
from django.contrib.auth import decorators as auth_decorators
from django.db import transaction

from . import forms as registry_forms, registration


@auth_decorators.login_required
@transaction.atomic
def evaluate_forms(request, regpoint_id, root_id):
    """
    This view gets called via an AJAX request to update configuration forms.
    """

    if request.method != 'POST':
        return http.HttpResponseNotAllowed(['POST'])

    regpoint = registration.point(regpoint_id)
    root = shortcuts.get_object_or_404(regpoint.model, pk=root_id) if root_id else None
    temp_root = False

    sid = transaction.savepoint()
    try:
        additional_flags = 0

        if root is None:
            # If there is no root then we must be just creating it.
            additional_flags = registry_forms.FORM_ROOT_CREATE
            # Create a fake temporary root (will not be saved because the transaction will be rolled back).
            temp_root = True
            root = regpoint.model()
            root.save()

        # TODO: Maybe actions should be registered and each action should have something like Action.name that would then call Action.prepare(...)
        actions = json.loads(request.POST.get('ACTIONS', ''))
        for action, options in actions.items():
            if action == 'defaults':
                additional_flags |= registry_forms.FORM_SET_DEFAULTS

                if options['value']:
                    additional_flags |= registry_forms.FORM_DEFAULTS_ENABLED
                else:
                    additional_flags &= ~registry_forms.FORM_DEFAULTS_ENABLED
            elif action == 'simple_mode':
                # Simple mode should also automatically enable defaults.
                if options['value']:
                    additional_flags |= registry_forms.FORM_SET_DEFAULTS | registry_forms.FORM_DEFAULTS_ENABLED

        # First perform partial validation and generate defaults.
        form_state = registry_forms.prepare_root_forms(
            regpoint,
            request,
            root,
            request.POST,
            flags=registry_forms.FORM_ONLY_DEFAULTS | additional_flags,
        )

        # Merge in client actions when available.
        changed = False
        for action, options in actions.items():
            if action == 'append':
                form_state.append_default_item(options['registry_id'], options['parent_id'])
                changed = True
            elif action == 'remove':
                form_state.remove_item(options['index'])
                changed = True
            elif action == 'simple_mode':
                form_state.set_using_simple_mode(options['value'])

        # Re-apply form defaults in case client actions have changed something.
        if changed:
            form_state.apply_form_defaults(regpoint, additional_flags & registry_forms.FORM_ROOT_CREATE)

        # Apply defaults and fully validate processed forms.
        _, forms = registry_forms.prepare_root_forms(
            regpoint,
            request,
            root,
            request.POST,
            save=True,
            form_state=form_state,
            flags=registry_forms.FORM_OUTPUT,
        )

        if temp_root:
            forms.root = None
    finally:
        try:
            transaction.savepoint_rollback(sid)
        except transaction.TransactionManagementError:
            # Rollback will fail if some query caused a database error and the whole
            # transaction is aborted anyway.
            pass

    # Render forms and return them.
    return shortcuts.render_to_response(
        'registry/forms.html',
        {'registry_forms': forms},
        context_instance=template.RequestContext(request),
    )
