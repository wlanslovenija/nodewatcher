from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.db import models
from django.utils.translation import ugettext as _
from wlanlj.nodes.models import Node, NodeType, NodeStatus, Subnet, SubnetStatus, APClient, Pool, WhitelistItem, Link, Event, EventSubscription, SubscriptionType, Project, EventCode, EventSource
from wlanlj.nodes.forms import RegisterNodeForm, UpdateNodeForm, AllocateSubnetForm, WhitelistMacForm, InfoStickerForm, EventSubscribeForm
from wlanlj.generator.models import Profile
from wlanlj.account.models import UserAccount
from wlanlj.policy.models import Policy, PolicyFamily, TrafficControlClass
from datetime import datetime
from wlanlj.nodes import ipcalc

def nodes(request):
  """
  Display a list of all current nodes and their status.
  """
  def type_ip_order(x, y):
    c = cmp(x.node_type, y.node_type)
    if c != 0:
      return c
    return cmp(long(ipcalc.IP(x.ip)), long(ipcalc.IP(y.ip)))
  nodes = list(Node.objects.all())
  nodes.sort(type_ip_order)
  return render_to_response('nodes/list.html',
    { 'nodes' : nodes },
    context_instance = RequestContext(request)
  )

def pools(request):
  """
  Displays IP allocation pools.
  """
  return render_to_response('nodes/pools.html',
    { 'pools' : Pool.objects.filter(parent = None).order_by('id') },
    context_instance = RequestContext(request)
  )

def pools_text(request):
  """
  Displays IP allocation pools as tab separated text values.
  """
  output = []
  for pool in Pool.objects.filter(parent = None).order_by('id'):
    output.append("%s\t%s\t%s" % (pool, pool.family_as_string(), pool.description))

  return HttpResponse("\n".join(output), content_type = "text/plain")

def statistics(request):
  """
  Displays some global statistics.
  """
  # Nodes by status
  node_count = len(Node.objects.all())
  others = node_count
  nodes_by_status = []
  for s in Node.objects.all().order_by('status').values('status').annotate(count = models.Count('ip')):
    nodes_by_status.append({ 'status' : NodeStatus.as_string(s['status']), 'count' : s['count'] })

  # Nodes by template usage
  templates_by_usage = []
  for t in Profile.objects.all().values('template__name').annotate(count = models.Count('node')).order_by('template__name'):
    templates_by_usage.append({ 'template' : t['template__name'], 'count' : t['count'] })
    others -= t['count']
  
  if others > 0:
    templates_by_usage.append({ 'template' : _("unknown"), 'count' : others, 'special' : True })

  # Nodes by project
  nodes_by_project = []
  others = 0
  for p in Node.objects.all().values('project__name').annotate(count = models.Count('ip')).order_by('project__id'):
    if not p['project__name']:
      others = p['count']
    else:
      nodes_by_project.append({ 'name' : p['project__name'], 'count' : p['count']})
  
  if others > 0:
    nodes_by_project.append({ 'name' : _("unknown"), 'count' : others, 'special' : True})

  return render_to_response('nodes/statistics.html',
    { 'node_count' : node_count,
      'nodes_by_status' : nodes_by_status,
      'nodes_by_status_length' : len(nodes_by_status),
      'nodes_by_status_element_width' : 100 / len(nodes_by_status),
      'nodes_by_project' : nodes_by_project,
      'nodes_warned' : len(Node.objects.filter(warnings = True)),
      'subnet_count' : len(Subnet.objects.all()),
      'clients_online' : len(APClient.objects.all()),
      'clients_ever' : Node.objects.aggregate(num = models.Sum('clients_so_far'))['num'],
      'external_ant' : len(Node.objects.filter(ant_external = True)),
      'template_usage' : templates_by_usage,
      'peers_avg' : Node.objects.filter(peers__gt = 0).aggregate(num = models.Avg('peers'))['num'] },
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
    { 'form' : form,
      'mobile_node_type' : NodeType.Mobile,
      'map_projects' : Project.objects.exclude(geo_lat = None).order_by("id") },
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
    form = UpdateNodeForm(node, request.POST)
    if form.is_valid():
      form.save(node, request.user)
      return HttpResponseRedirect("/nodes/node/" + node.ip)
  else:
    p = {
      'name'                : node.name,
      'ip'                  : node.ip,
      'location'            : node.location,
      'geo_lat'             : node.geo_lat,
      'geo_long'            : node.geo_long,
      'ant_external'        : node.ant_external,
      'ant_polarization'    : node.ant_polarization,
      'ant_type'            : node.ant_type,
      'owner'               : node.owner.id,
      'project'             : node.project.id,
      'system_node'         : node.system_node,
      'border_router'       : node.border_router,
      'node_type'           : node.node_type,
      'notes'               : node.notes,
      'url'                 : node.url,
      'redundancy_req'      : node.redundancy_req
    }

    try:
      p.update({
        'tc_ingress'          : node.gw_policy.get(addr = node.vpn_mac_conf, family = PolicyFamily.Ethernet).tc_class.id
      })
    except Policy.DoesNotExist:
      pass

    try:
      p.update({
        'template'            : node.profile.template.id,
        'use_vpn'             : node.profile.use_vpn,
        'tc_egress'           : TrafficControlClass.objects.get(bandwidth = node.profile.vpn_egress_limit).id if node.profile.vpn_egress_limit else None,
        'use_captive_portal'  : node.profile.use_captive_portal,
        'wan_dhcp'            : node.profile.wan_dhcp,
        'wan_ip'              : "%s/%s" % (node.profile.wan_ip, node.profile.wan_cidr) if node.profile.wan_ip and node.profile.wan_cidr else None,
        'wan_gw'              : node.profile.wan_gw,
        'root_pass'           : node.profile.root_pass,
        'channel'             : node.profile.channel,
        'lan_bridge'          : node.profile.lan_bridge,
        'ant_conn'            : node.profile.antenna,
        'optional_packages'   : [x.id for x in node.profile.optional_packages.all()]
      })
    except Profile.DoesNotExist:
      p.update({
        'template'            : None,
        'use_vpn'             : True,
        'use_captive_portal'  : True,
        'wan_dhcp'            : True,
        'wan_ip'              : '',
        'wan_gw'              : '',
        'root_pass'           : '',
        'channel'             : node.project.channel,
        'lan_bridge'          : False,
        'ant_conn'            : 3,
        'optional_packages'   : []
      })

    form = UpdateNodeForm(node, p)

  return render_to_response('nodes/edit.html',
    { 'form' : form,
      'node' : node,
      'mobile_node_type' : NodeType.Mobile,
      'map_projects' : Project.objects.exclude(geo_lat = None).order_by("id") },
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
def node_reset(request, node_ip):
  """
  Displays a form where the user can confirm node data reset. If
  confirmed, node data is reset and node is moved into pending
  state.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  if request.method == 'POST':
    # Reset confirmed
    if node.status in (NodeStatus.Down, NodeStatus.Pending):
      node.status = NodeStatus.Pending
      node.reset()
      node.save()

      return HttpResponseRedirect("/nodes/node/%s" % node.ip)

  return render_to_response('nodes/reset.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_remove(request, node_ip):
  """
  Displays node info.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if request.method == 'POST':
    # Generate node removed event and remove node
    Event.create_event(node, EventCode.NodeRemoved, '', EventSource.NodeDatabase)
    node.delete()
    return HttpResponseRedirect("/nodes/my_nodes")
  
  return render_to_response('nodes/remove.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )


@login_required
def node_allocate_subnet(request, node_ip):
  """
  Displays node info.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.status == NodeStatus.Invalid or (node.owner != request.user and not request.user.is_staff):
    raise Http404
 
  if request.method == 'POST':
    form = AllocateSubnetForm(node, request.POST)
    if form.is_valid():
      form.save(node)
      return HttpResponseRedirect("/nodes/node/" + node.ip)
  else:
    form = AllocateSubnetForm(node)

  return render_to_response('nodes/allocate_subnet.html',
    { 'form' : form,
      'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_deallocate_subnet(request, subnet_id):
  """
  Displays node info.
  """
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  node = subnet.node
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if request.method == 'POST':
    if subnet.is_wifi and not request.user.is_staff:
      raise Http404

    subnet.delete()
    return HttpResponseRedirect("/nodes/node/%s" % node.ip)

  return render_to_response('nodes/deallocate_subnet.html',
    { 'node' : node,
      'subnet' : subnet },
    context_instance = RequestContext(request)
  )

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
  # Remove duplicate links
  links = []
  existing = {}

  for link in Link.objects.all():
    if (link.dst, link.src) not in existing or link.etx > existing[(link.dst, link.src)]:
      existing[(link.src, link.dst)] = link.etx
      links.append(link)

  return render_to_response('nodes/map.html',
    { 'nodes' : Node.objects.all(),
      'links' : links,
      'projects' : Project.objects.exclude(geo_lat = None).order_by("id") },
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
  show_errors = True

  if request.method == 'POST':
    form = InfoStickerForm(request.POST)
    if form.is_valid():
      return HttpResponseRedirect(form.save(user))
  else:
    form = InfoStickerForm({
      'name'    : user.name,
      'phone'   : user.phone,
      'project' : user.project.id if user.project else 0
    })

    show_errors = False

  return render_to_response('nodes/sticker.html',
    { 'form' : form,
      'show_errors' : show_errors },
    context_instance = RequestContext(request)
  )

def global_events(request):
  """
  Display a list of global mesh events.
  """
  return render_to_response('nodes/global_events.html',
    { 'events' : Event.objects.all().order_by('-id')[0:30] },
    context_instance = RequestContext(request)
  )

@login_required
def event_list(request):
  """
  Display a list of current user's events.
  """
  return render_to_response('nodes/event_list.html',
    { 'events' : Event.objects.filter(node__owner = request.user).order_by('-id')[0:30],
      'subscriptions' : EventSubscription.objects.filter(user = request.user) },
    context_instance = RequestContext(request)
  )

@login_required
def event_subscribe(request):
  """
  Display a form for subscribing to an event.
  """
  if request.method == 'POST':
    form = EventSubscribeForm(request.POST)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect("/nodes/events")
  else:
    form = EventSubscribeForm()

  return render_to_response('nodes/event_subscribe.html',
    { 'form' : form,
      'single_node_type' : SubscriptionType.SingleNode },
    context_instance = RequestContext(request)
  )

@login_required
def event_unsubscribe(request, subscription_id):
  """
  Removes event subscription.
  """
  s = get_object_or_404(EventSubscription, pk = subscription_id)
  if s.user != request.user and not request.user.is_staff:
    raise Http404
  
  s.delete()

  return HttpResponseRedirect("/nodes/events")

@login_required
def package_list(request, node_ip):
  """
  Display a list of node's installed packages.
  """
  node = get_object_or_404(Node, pk = node_ip)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  return render_to_response('nodes/installed_packages.html',
    { 'packages' : node.installedpackage_set.all().order_by('name'),
      'node'  : node },
    context_instance = RequestContext(request)
  )

