import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import safestring

from registry import forms as registry_forms
from web.nodes import decorators

@login_required
@decorators.node_argument
def evaluate_forms(request, node):
  """
  This view gets called via an AJAX request to evaluate rules.
  """
  if request.method != 'POST':
    return HttpResponse('')
  
  try:
    sid = transaction.savepoint()
    
    # First perform partial validation and rule evaluation
    actions = registry_forms.prepare_forms_for_node(
      node,
      request.POST,
      only_rules = True
    )
    
    # Merge in client actions when available
    try:
      for action, cls_id in json.loads(request.POST['ACTIONS']).iteritems():
        if action == 'append':
          actions.setdefault(cls_id, []).insert(0, ('append', None, {}))
        elif action == 'remove_last':
          actions.setdefault(cls_id, []).insert(0, ('remove_last',))
    except AttributeError:
      pass
    
    # Apply rules and fully validate processed forms
    _, forms = registry_forms.prepare_forms_for_node(
      node,
      request.POST,
      save = True,
      actions = actions
    )
  finally:
    transaction.savepoint_rollback(sid)
    
  # Render forms and return them
  return render_to_response(
    'registry/forms.html',
    {
      'registry_forms' : forms,
      'eval_state' : safestring.mark_safe(json.dumps(actions["STATE"])),
      'node' : node
    },
    context_instance = RequestContext(request)
  )

