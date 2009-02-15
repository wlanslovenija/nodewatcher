from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from ljwifi.nodes.models import Node
from ljwifi.generator.queue import queue_generator_job

@login_required
def request(request, node_ip):
  """
  Displays a confirmation form.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  return render_to_response('generator/generate.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def generate(request, node_ip):
  """
  Generates an image for the specified node.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if not node.has_allocated_subnets():
    return HttpResponseRedirect("/generator/request/" + node_ip)

  # Actually queue the job
  queue_generator_job(node)

  return render_to_response('generator/please_wait.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

