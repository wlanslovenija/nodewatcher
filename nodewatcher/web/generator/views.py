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
      form.save(node)
      queue_generator_job(node)

      return render_to_response('generator/please_wait.html',
        { 'node' : node },
        context_instance = RequestContext(request)
      )
  else:
    p = {
      'wan_dhcp'  : node.profile.wan_dhcp,
      'wan_gw'    : node.profile.wan_gw,
      'antenna'   : node.profile.antenna
    }

    if node.profile.wan_ip and node.profile.wan_cidr:
      p['wan_ip'] = "%s/%s" % (node.profile.wan_ip, node.profile.wan_cidr)

    form = GenerateImageForm(p)

  return render_to_response('generator/generate.html',
    { 'node'  : node,
      'form'  : form },
    context_instance = RequestContext(request)
  )

