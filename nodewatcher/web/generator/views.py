from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from wlanlj.nodes.models import Node
from wlanlj.generator.queue import queue_generator_job
from wlanlj.generator.forms import GenerateImageForm

@login_required
def request(request, node_ip):
  """
  Displays a confirmation form.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  if request.method == 'POST':
    form = GenerateImageForm(request.POST)
    if form.is_valid():
      email_user = form.save(node)
      queue_generator_job(node, email_user)

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

