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

      if settings.ENABLE_IMAGE_GENERATOR and not settings.IMAGE_GENERATOR_SUSPENDED:
        email_user = form.save(node)
        queue_generator_job(node, email_user, form.cleaned_data['config_only'])

      return render_to_response('generator/please_wait.html',
        { 'node' : node,
          'image_generator_enabled' : settings.ENABLE_IMAGE_GENERATOR,
          'image_generator_suspended' : settings.IMAGE_GENERATOR_SUSPENDED },
        context_instance = RequestContext(request)
      )
  else:
    form = GenerateImageForm(initial = {
      'email_user'  : node.owner.id
    })

  return render_to_response('generator/generate.html',
    { 'node'  : node,
      'form'  : form },
    context_instance = RequestContext(request)
  )

