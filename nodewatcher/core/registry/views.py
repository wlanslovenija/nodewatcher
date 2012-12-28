import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import safestring

from nodewatcher.core.registry import forms as registry_forms
from nodewatcher.core.registry import registration

@login_required
def evaluate_forms(request, regpoint_id, root_id):
    """
    This view gets called via an AJAX request to evaluate rules.
    """
    if request.method != 'POST':
        return HttpResponse('')

    regpoint = registration.point(regpoint_id)
    root = get_object_or_404(regpoint.model, pk = root_id) if root_id else None
    temp_root = False

    try:
        sid = transaction.savepoint()
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
          only_rules = True
        )

        # Merge in client actions when available
        try:
            # TODO maybe actions should be registered and each action should have something
            #      like Action.name that would then call Action.prepare(...)
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
          save = True,
          actions = actions,
          current_config = partial_config
        )
    finally:
        transaction.savepoint_rollback(sid)

    # Render forms and return them
    return render_to_response(
        'registry/forms.html',
      {
        'registry_forms' : forms,
        'eval_state' : safestring.mark_safe(json.dumps(actions["STATE"])),
        'registry_root' : root if not temp_root else None,
        'registry_regpoint' : regpoint_id
      },
      context_instance = RequestContext(request)
    )
