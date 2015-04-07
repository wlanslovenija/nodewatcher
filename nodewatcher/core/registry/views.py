import json

from django import http, shortcuts, template
from django.contrib.auth import decorators as auth_decorators
from django.db import transaction

from . import forms as registry_forms, registration


@auth_decorators.login_required
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
        if root is None:
            # Create a fake temporary root (will not be saved because the transaction will be rolled back).
            temp_root = True
            root = regpoint.model()
            root.save()

        # First perform partial validation and generate defaults.
        form_state = registry_forms.prepare_root_forms(
            regpoint,
            request,
            root,
            request.POST,
            flags=registry_forms.FORM_ONLY_DEFAULTS,
        )

        # Merge in client actions when available.
        try:
            # TODO: Maybe actions should be registered and each action should have something like Action.name that would then call Action.prepare(...)
            for action, options in json.loads(request.POST['ACTIONS']).iteritems():
                if action == 'append':
                    form_state.append_default_item(options['registry_id'], options['parent_id'])
                elif action == 'remove':
                    form_state.remove_item(options['index'])
        except AttributeError:
            pass

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
        transaction.savepoint_rollback(sid)

    # Render forms and return them.
    return shortcuts.render_to_response(
        'registry/forms.html',
        {'registry_forms': forms},
        context_instance=template.RequestContext(request),
    )
