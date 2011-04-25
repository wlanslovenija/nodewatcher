from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

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
    
    # TODO Apply rules
    
    # Fully validate processed forms
    _, forms = registry_forms.prepare_forms_for_node(
      node,
      request.POST,
      save = True
    )
  finally:
    transaction.savepoint_rollback(sid)
    
  # Render forms and return them
  return render_to_response(
    'registry/forms.html',
    {
      'registry_forms' : forms,
      'node' : node
    },
    context_instance = RequestContext(request)
  )

