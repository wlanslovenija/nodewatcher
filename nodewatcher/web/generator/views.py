from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings

from web.account import decorators as account_decorators
from web.nodes import decorators
from web.nodes.models import Node
from web.generator.models import Profile
from web.generator.queue import queue_generator_job
from web.generator.forms import GenerateImageForm

@account_decorators.authenticated_required
@decorators.node_argument
def request(request, node):
  """
  Displays a confirmation form.
  """
  if not node.is_current_owner(request):
    raise Http404

  try:
    profile = node.profile
  except Profile.DoesNotExist:
    raise Http404

  if request.method == 'POST':
    form = GenerateImageForm(request.POST)
    if form.is_valid():

      if getattr(settings, 'IMAGE_GENERATOR_ENABLED', False) and not getattr(settings, 'IMAGE_GENERATOR_SUSPENDED', False):
        email_user = form.save(request, node)
        queue_generator_job(node, email_user, form.cleaned_data['config_only'])

      return render_to_response('generator/please_wait.html',
        { 'node' : node,
          'image_generator_enabled' : getattr(settings, 'IMAGE_GENERATOR_ENABLED', False),
          'image_generator_suspended' : getattr(settings, 'IMAGE_GENERATOR_SUSPENDED', False) },
        context_instance = RequestContext(request)
      )
  else:
    form = GenerateImageForm(initial = {
      'email_user'  : node.owner.pk,
    })

  return render_to_response('generator/generate.html',
    { 'node'  : node,
      'form'  : form },
    context_instance = RequestContext(request)
  )

