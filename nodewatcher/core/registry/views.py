import json

from django import http, shortcuts, template
from django.contrib.auth import decorators as auth_decorators
from django.db import transaction
from django.utils import safestring

from . import forms as registry_forms, registration


@auth_decorators.login_required
def evaluate_forms(request, regpoint_id, root_id):
    """
    This view gets called via an AJAX request to evaluate rules.
    """

    if request.method != 'POST':
        return http.HttpResponse('')

    regpoint = registration.point(regpoint_id)
    root = shortcuts.get_object_or_404(regpoint.model, pk=root_id) if root_id else None
    temp_root = False

    sid = transaction.savepoint()
    try:
        if root is None:
            # Create a fake temporary root (will not be saved because the transaction will
            # be rolled back)
            temp_root = True
            root = regpoint.model()
            root.save()

        # First perform partial validation and rule evaluation
        actions, partial_config = registry_forms.prepare_forms_for_regpoint_root(
            regpoint,
            request,
            root,
            request.POST,
            only_rules=True,
        )

        # Merge in client actions when available
        try:
            # TODO: Maybe actions should be registered and each action should have something like Action.name that would then call Action.prepare(...)
            for action, prefix in json.loads(request.POST['ACTIONS']).iteritems():
                if action == 'append':
                    actions.setdefault(prefix, []).insert(0, registry_forms.AppendFormAction(None))
                elif action == 'remove_last':
                    actions.setdefault(prefix, []).insert(0, registry_forms.RemoveLastFormAction())
        except AttributeError:
            pass

        # Apply rules and fully validate processed forms
        _, forms = registry_forms.prepare_forms_for_regpoint_root(
            regpoint,
            request,
            root,
            request.POST,
            save=True,
            actions=actions,
            current_config=partial_config,
        )
    finally:
        transaction.savepoint_rollback(sid)

    # Render forms and return them
    return shortcuts.render_to_response(
        'registry/forms.html',
        {
            'registry_forms': forms,
            'eval_state': safestring.mark_safe(json.dumps(actions["STATE"])),
            'registry_root': root if not temp_root else None,
            'registry_regpoint': regpoint_id,
        },
        context_instance=template.RequestContext(request),
    )
