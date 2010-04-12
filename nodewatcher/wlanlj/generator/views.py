from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from wlanlj.nodes.models import Node
from wlanlj.generator.models import Profile
from wlanlj.generator.queue import queue_generator_job
from wlanlj.generator.forms import GenerateImageForm

@login_required
def request(request, node):
  """
  Displays a confirmation form.
  """
  node = get_object_or_404(Node, pk = node)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  try:
    profile = node.profile
  except Profile.DoesNotExist:
    raise Http404

  if request.method == 'POST':
    form = GenerateImageForm(request.POST)
    if form.is_valid():

      if not settings.ENABLE_IMAGE_GENERATOR:
        request.user.message_set.create(message=_("The generator is disabled in the settings. Enable it by setting ENABLE_IMAGE_GENERATOR variable to TRUE."))
      else:
        email_user = form.save(node)
        queue_generator_job(node, email_user, form.cleaned_data['config_only'])
        request.user.message_set.create(message=_("Your image generation request has been successfully queued in our system. "))

      return render_to_response('generator/please_wait.html',
        { 'node' : node },
        context_instance = RequestContext(request)
      )
  else:
    form = GenerateImageForm({
      'email_user'  : node.owner.id
    })

  return render_to_response('generator/generate.html',
    { 'node'  : node,
      'form'  : form },
    context_instance = RequestContext(request)
  )

