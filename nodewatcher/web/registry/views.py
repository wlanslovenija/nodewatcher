from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from registry import forms as registry_forms
from web.nodes import decorators

@login_required
@decorators.node_argument
def evaluate_forms(request, node):
  """
  This view gets called via an AJAX request to evaluate rules.
  """
  if request.method != 'POST':
    return HttpResponse('', content_type = 'text/javascript')
  
  actions = registry_forms.prepare_forms_for_node(
    node,
    request.POST,
    save = True,
    only_rules = True
  )
  
  return HttpResponse("\n".join(actions), content_type = 'text/javascript')

