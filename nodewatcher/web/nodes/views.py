from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from wlanlj.nodes.models import Node, NodeStatus, Subnet, SubnetStatus, APClient, Pool, WhitelistItem, Link
from wlanlj.nodes.forms import RegisterNodeForm, UpdateNodeForm, AllocateSubnetForm, WhitelistMacForm, InfoStickerForm
from wlanlj.account.models import UserAccount
from datetime import datetime

def nodes(request):
  """
  Display a list of all current nodes and their status.
  """
  nodes = Node.objects.all().order_by('-system_node', 'ip')
  return render_to_response('nodes/list.html',
    { 'nodes' : nodes },
    context_instance = RequestContext(request)
  )

@login_required
def my_nodes(request):
  """
  Display a list of current user's nodes.
  """
  nodes = request.user.node_set.order_by('ip')
  whitelist = request.user.whitelistitem_set.order_by('mac')
  return render_to_response('nodes/my.html',
    { 'nodes' : nodes,
      'whitelist' : whitelist },
    context_instance = RequestContext(request)
  )

@login_required
def node_new(request):
  """
  Display a form for registering a new node.
  """
  if request.method == 'POST':
    form = RegisterNodeForm(request.POST)
    if form.is_valid():
      node = form.save(request.user)
      return HttpResponseRedirect("/nodes/node/" + node.ip)
  else:
    form = RegisterNodeForm()

  return render_to_response('nodes/new.html',
    { 'form' : form },
    context_instance = RequestContext(request)
  )

@login_required
def node_edit(request, node_ip):
  """
  Display a form for registering a new node.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.status == NodeStatus.Invalid or (node.owner != request.user and not request.user.is_staff):
    raise Http404
  
  if request.method == 'POST':
    form = UpdateNodeForm(request.POST)
    if form.is_valid():
      form.save(node, request.user)
      return HttpResponseRedirect("/nodes/node/" + node.ip)
  else:
    form = UpdateNodeForm({
      'name'                : node.name,
      'ip'                  : node.ip,
      'location'            : node.location,
      'geo_lat'             : node.geo_lat,
      'geo_long'            : node.geo_long,
      'ant_external'        : node.ant_external,
      'ant_polarization'    : node.ant_polarization,
      'ant_type'            : node.ant_type,
      'owner'               : node.owner.id,
      'system_node'         : node.system_node,
      'border_router'       : node.border_router,
      'template'            : node.profile.template.id,
      'use_vpn'             : node.profile.use_vpn,
      'use_captive_portal'  : node.profile.use_captive_portal,
      'root_pass'           : node.profile.root_pass,
      'channel'             : node.profile.channel
    })

  return render_to_response('nodes/edit.html',
    { 'form' : form,
      'node' : node },
    context_instance = RequestContext(request)
  )

def node(request, node_ip = None):
  """
  Displays node info.
  """
  if not node_ip:
    raise Http404
  
  node = get_object_or_404(Node, pk = node_ip)
  
  return render_to_response('nodes/node.html',
    { 'node' : node ,
      'current_owner' : node.status != NodeStatus.Invalid and (node.owner == request.user or request.user.is_staff) },
    context_instance = RequestContext(request)
  )

@login_required
def node_remove(request, node_ip = None):
  """
  Displays node info.
  """
  if not node_ip:
    raise Http404
  
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  return render_to_response('nodes/remove.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_do_remove(request, node_ip = None):
  """
  Displays node info.
  """
  if not node_ip:
    raise Http404
  
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  node.delete()

  return HttpResponseRedirect("/nodes/my_nodes")

@login_required
def node_allocate_subnet(request, node_ip = None):
  """
  Displays node info.
  """
  if not node_ip:
    raise Http404
  
  node = get_object_or_404(Node, pk = node_ip)
  if node.status == NodeStatus.Invalid or (node.owner != request.user and not request.user.is_staff):
    raise Http404
 
  if request.method == 'POST':
    form = AllocateSubnetForm(request.POST)
    if form.is_valid():
      form.save(node)
      return HttpResponseRedirect("/nodes/node/" + node.ip)
  else:
    form = AllocateSubnetForm()

  return render_to_response('nodes/allocate_subnet.html',
    { 'form' : form,
      'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_deallocate_subnet(request, subnet_id = None):
  """
  Displays node info.
  """
  if not subnet_id:
    raise Http404
  
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  node = subnet.node
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  return render_to_response('nodes/deallocate_subnet.html',
    { 'node' : node,
      'subnet' : subnet },
    context_instance = RequestContext(request)
  )

@login_required
def node_do_deallocate_subnet(request, subnet_id = None):
  """
  Displays node info.
  """
  if not subnet_id:
    raise Http404
  
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  node = subnet.node
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  subnet.delete()

  return HttpResponseRedirect("/nodes/node/" + node.ip)

@login_required
def whitelist_mac(request):
  """
  Display a form for whitelisting a MAC address.
  """
  if request.method == 'POST':
    form = WhitelistMacForm(request.POST)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect("/nodes/my_nodes")
  else:
    form = WhitelistMacForm()

  return render_to_response('nodes/whitelist_mac.html',
    { 'form' : form },
    context_instance = RequestContext(request)
  )

@login_required
def unwhitelist_mac(request, item_id):
  """
  Removes a whitelisted MAC address.
  """
  item = get_object_or_404(WhitelistItem, pk = item_id)
  if item.owner != request.user and not request.user.is_staff:
    raise Http404
  
  item.delete()
  return HttpResponseRedirect("/nodes/my_nodes")

def whitelist(request):
  """
  Displays a list of whitelisted addresses.
  """
  output = []
  for item in WhitelistItem.objects.all():
    output.append(item.mac)

  return HttpResponse("\n".join(output), content_type = "text/plain")

def topology(request):
  """
  Displays mesh topology.
  """
  return render_to_response('nodes/topology.html', {},
    context_instance = RequestContext(request)
  )

def map(request):
  """
  Displays mesh map.
  """
  return render_to_response('nodes/map.html',
    { 'nodes' : Node.objects.all(),
      'links' : Link.objects.all() },
    context_instance = RequestContext(request)
  )

def gcl(request):
  """
  Displays the global client list.
  """
  clients = APClient.objects.all().order_by('node')
  return render_to_response('nodes/gcl.html',
    { 'clients' : clients },
    context_instance = RequestContext(request)
  )

@login_required
def sticker(request):
  """
  Display a form for generating an info sticker.
  """
  user = UserAccount.for_user(request.user)

  if request.method == 'POST':
    form = InfoStickerForm(request.POST)
    if form.is_valid():
      return HttpResponseRedirect(form.save(user))
  else:
    form = InfoStickerForm({
      'name'  : user.name,
      'phone' : user.phone
    })

  return render_to_response('nodes/sticker.html',
    { 'form' : form },
    context_instance = RequestContext(request)
  )

