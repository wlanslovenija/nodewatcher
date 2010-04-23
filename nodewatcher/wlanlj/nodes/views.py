from django.conf import settings
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.db import models, transaction
from django.forms import forms
from django.utils.translation import ugettext as _
from wlanlj.nodes.models import Node, NodeType, NodeStatus, Subnet, SubnetStatus, APClient, Pool, WhitelistItem, Link, Event, EventSubscription, SubscriptionType, Project, EventCode, EventSource, GraphItemNP, GraphType, PoolStatus
from wlanlj.nodes.forms import RegisterNodeForm, UpdateNodeForm, AllocateSubnetForm, WhitelistMacForm, InfoStickerForm, EventSubscribeForm, RenumberForm, RenumberAction, EditSubnetForm
from wlanlj.nodes.common import ValidationWarning
from wlanlj.generator.models import Profile
from wlanlj.account.models import UserAccount
from wlanlj.policy.models import Policy, PolicyFamily, TrafficControlClass
from datetime import datetime
from wlanlj.nodes import ipcalc
from django.core.urlresolvers import reverse

def nodes(request):
  """
  Display a list of all current nodes and their status.
  """
  # TODO: #362
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
  # TODO: #362
  def ip_order(x, y):
    return cmp(long(ipcalc.IP(str(x.ip_subnet))), long(ipcalc.IP(str(y.ip_subnet))))
  pools = list(Pool.objects.filter(parent = None))
  pools.sort(ip_order)
  return render_to_response('nodes/pools.html',
    { 'pools' : pools },
    context_instance = RequestContext(request)
  )

def pools_text(request):
  """
  Displays IP allocation pools as tab separated text values.
  """
  output = []
  for pool in Pool.objects.filter(parent = None).order_by('id'):
    output.append("%s\t%s\t%s" % (pool.ip_subnet, pool.family_as_string(), pool.description))

  return HttpResponse("\n".join(output), content_type = "text/plain")

def statistics(request):
  """
  Displays some global statistics.
  """
  # Nodes by status
  node_count = Node.objects.all().count()
  nodes_by_status = []
  for s in Node.objects.exclude(node_type = NodeType.Test).order_by('status').values('status').annotate(count = models.Count('ip')):
    nodes_by_status.append({ 'status' : NodeStatus.as_string(s['status']), 'count' : s['count'] })

  # Nodes by template usage
  others = Node.objects.exclude(node_type = NodeType.Test).count()
  templates_by_usage = []
  for t in Profile.objects.exclude(node__node_type = NodeType.Test).values('template__name').annotate(count = models.Count('node')).order_by('template__name'):
    templates_by_usage.append({ 'template' : t['template__name'], 'count' : t['count'] })
    others -= t['count']
  
  if others > 0:
    templates_by_usage.append({ 'template' : _("unknown"), 'count' : others, 'special' : True })

  # Nodes by project
  nodes_by_project = []
  others = 0
  for p in Node.objects.exclude(node_type = NodeType.Test).values('project__name').annotate(count = models.Count('ip')).order_by('project__id'):
    if not p['project__name']:
      others = p['count']
    else:
      nodes_by_project.append({ 'name' : p['project__name'], 'count' : p['count']})
  
  if others > 0:
    nodes_by_project.append({ 'name' : _("unknown"), 'count' : others, 'special' : True})

  return render_to_response('nodes/statistics.html',
    { 'node_count' : node_count,
      'nodes_by_status' : nodes_by_status,
      'nodes_by_project' : nodes_by_project,
      'nodes_warned' : Node.objects.filter(warnings = True).exclude(node_type = NodeType.Test).count(),
      'nodes_test' : Node.objects.filter(node_type = NodeType.Test).count(),
      'subnet_count' : Subnet.objects.all().count(),
      'clients_online' : APClient.objects.all().count(),
      'clients_ever' : Node.objects.aggregate(num = models.Sum('clients_so_far'))['num'],
      'external_ant' : Node.objects.filter(ant_external = True).exclude(node_type = NodeType.Test).count(),
      'template_usage' : templates_by_usage,
      'peers_avg' : Node.objects.filter(peers__gt = 0).aggregate(num = models.Avg('peers'))['num'],
      'graphs' : [
        GraphItemNP(1, GraphType.NodesByStatus, "global_nodes_by_status.png", "Nodes By Status"),
        GraphItemNP(2, GraphType.Clients, "global_client_count.png", "Global Client Count"),
        GraphItemNP(3, GraphType.GatewayTraffic, "global_replicator_traffic.png", "replicator - Traffic")
      ],
      'timespans' : [prefix for prefix, name in settings.GRAPH_TIMESPANS]
    },
    context_instance = RequestContext(request)
  )

@login_required
def my_nodes(request):
  """
  Display a list of current user's nodes.
  """
  # TODO: #362
  nodes = request.user.node_set.order_by('ip')
  
  return render_to_response('nodes/my.html',
    { 'nodes' : nodes },
    context_instance = RequestContext(request)
  )

@login_required
def node_new(request):
  """
  Display a form for registering a new node.
  """
  if request.method == 'POST':
    form = RegisterNodeForm(request.POST)
    if form.is_valid() and form.save(request.user):
      return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = form.node.pk)))
  else:
    form = RegisterNodeForm()

  return render_to_response('nodes/new.html',
    { 'form' : form,
      'mobile_node_type' : NodeType.Mobile,
      'projects' : Project.objects.all().order_by("id") },
    context_instance = RequestContext(request)
  )

@login_required
def node_edit(request, node):
  """
  Display a form for registering a new node.
  """
  node = get_object_or_404(Node, pk = node)
  if node.status == NodeStatus.Invalid or (node.owner != request.user and not request.user.is_staff):
    raise Http404
  
  if request.method == 'POST':
    form = UpdateNodeForm(node, request.POST)
    if form.is_valid() and form.save(node, request.user):
      if form.requires_firmware_update:
        return render_to_response('nodes/firmware_update_needed.html', {
            'node' : node
          },
          context_instance = RequestContext(request)
        )
      else:
        return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))
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

    form = UpdateNodeForm(node, initial = p)

  return render_to_response('nodes/edit.html',
    { 'form' : form,
      'node' : node,
      'mobile_node_type' : NodeType.Mobile,
      'projects' : Project.objects.all().order_by("id") },
    context_instance = RequestContext(request)
  )

def node(request, node):
  """
  Displays node info.
  """
  try:
    node = Node.objects.get(pk = node)
  except Node.DoesNotExist:
    try:
      node = Node.objects.get(ip = node)
    except Node.DoesNotExist:
      node = get_object_or_404(Node, name = node)
  
  return render_to_response('nodes/node.html',
    { 'node' : node ,
      'timespans' : [prefix for prefix, name in settings.GRAPH_TIMESPANS],
      'current_owner' : node.status != NodeStatus.Invalid and (node.owner == request.user or request.user.is_staff) },
    context_instance = RequestContext(request)
  )

@login_required
def node_reset(request, node):
  """
  Displays a form where the user can confirm node data reset. If
  confirmed, node data is reset and node is moved into pending
  state.
  """
  node = get_object_or_404(Node, pk = node)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  if request.method == 'POST':
    # Reset confirmed
    if node.is_resettable():
      node.status = NodeStatus.Pending
      node.reset()
      node.save()

      return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))

  return render_to_response('nodes/reset.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_remove(request, node):
  """
  Displays node info.
  """
  node = get_object_or_404(Node, pk = node)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if request.method == 'POST':
    # Generate node removed event and remove node
    Event.create_event(node, EventCode.NodeRemoved, '', EventSource.NodeDatabase,
                       data = 'Removed by: %s' % request.user.username)
    node.delete()
    return HttpResponseRedirect(reverse("my_nodes"))
  
  return render_to_response('nodes/remove.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@login_required
def node_renumber(request, node):
  """
  Renumbers a given node.
  """
  node = get_object_or_404(Node, pk = node)
  if (node.owner != request.user and not request.user.is_staff) or node.is_invalid():
    raise Http404
  
  if request.method == 'POST':
    form = RenumberForm(request.user, node, request.POST)
    try:
      sid = transaction.savepoint()
      if form.is_valid():
        form.save()
        transaction.savepoint_commit(sid)
        return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))
    except ValidationWarning:
      # We must display a warning before the user may continue; node must be reloaded
      # because savepoint has been rolled back and any modifications have actually been
      # invalidated (but remain in memory)
      transaction.savepoint_rollback(sid)
      node = Node.objects.get(pk = node.pk)
    except:
      # Something went wrong
      transaction.savepoint_rollback(sid)
      error = forms.ValidationError(_("Renumbering cannot be completed because at least one target pool is incompatible with given subnet prefix length!"))
      form._errors[forms.NON_FIELD_ERRORS] = form.error_class(error.messages)
  else:
    form = RenumberForm(request.user, node)
  
  return render_to_response('nodes/renumber.html',
    { 'node' : node,
      'form' : form,
      'renumber_action_manual' : RenumberAction.SetManually },
    context_instance = RequestContext(request)
  )

@login_required
def node_allocate_subnet(request, node):
  """
  Displays node info.
  """
  node = get_object_or_404(Node, pk = node)
  if node.status == NodeStatus.Invalid or (node.owner != request.user and not request.user.is_staff):
    raise Http404
 
  if request.method == 'POST':
    form = AllocateSubnetForm(node, request.POST)
    if form.is_valid() and form.save(node):
      return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))
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
  Removes a subnet.
  """
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  node = subnet.node
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if request.method == 'POST':
    if subnet.is_primary():
      raise Http404

    subnet.delete()
    return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))

  return render_to_response('nodes/deallocate_subnet.html',
    { 'node' : node,
      'subnet' : subnet },
    context_instance = RequestContext(request)
  )

@login_required
def node_edit_subnet(request, subnet_id):
  """
  Edits a subnet.
  """
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  node = subnet.node
  if node.owner != request.user and not request.user.is_staff:
    raise Http404
  
  if request.method == 'POST':
    form = EditSubnetForm(node, request.POST)
    if form.is_valid():
      subnet.description = form.cleaned_data.get('description')
      subnet.gen_dhcp = form.cleaned_data.get('dhcp')
      
      if not subnet.is_primary():
        # One can't reassign the primary subnet, as it should always be on the
        # mesh interface!
        subnet.gen_iface_type = form.cleaned_data.get('iface_type')
      
      subnet.save()
      return HttpResponseRedirect(reverse("view_node", kwargs = dict(node = node.pk)))
  else:
    form = EditSubnetForm(node, initial = {
      'description' : subnet.description,
      'iface_type' : subnet.gen_iface_type,
      'dhcp' : subnet.gen_dhcp
    })

  return render_to_response('nodes/edit_subnet.html',
    { 'node'   : node,
      'subnet' : subnet,
      'form'   : form },
    context_instance = RequestContext(request)
  )

@login_required
def whitelisted_mac(request):
  """
  Display a form for whitelisting a MAC address.
  """
  if request.method == 'POST':
    form = WhitelistMacForm(request.POST)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect("/nodes/whitelisted_mac")
  else:
    form = WhitelistMacForm()

  whitelist = request.user.whitelistitem_set.order_by('mac')
  return render_to_response('nodes/whitelisted_mac.html',
    { 'form' : form,
      'whitelist' : whitelist },
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
  return HttpResponseRedirect("/nodes/whitelisted_mac")

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
      'default_lat' : settings.GOOGLE_MAPS_DEFAULT_LAT,
      'default_long' : settings.GOOGLE_MAPS_DEFAULT_LONG,
      'default_zoom' : settings.GOOGLE_MAPS_DEFAULT_ZOOM,
      'projects' : Project.objects.all().order_by("id") },
    context_instance = RequestContext(request)
  )

def gcl(request):
  """
  Displays the global client list.
  """
  # TODO: #362
  clients = APClient.objects.all().order_by('node__ip', 'connected_at')
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
    { 'events' : Event.objects.all().order_by('-timestamp', '-id')[0:30] },
    context_instance = RequestContext(request)
  )

def node_events(request, node):
  """
  Display a list of a node's events.
  """
  node = get_object_or_404(Node, pk = node)
  return render_to_response('nodes/node_events.html',
    { 'node' : node,
      'events' : node.event_set.order_by('-timestamp', '-id')[0:30] },
    context_instance = RequestContext(request)
  )


@login_required
def event_list(request):
  """
  Display a list of current user's events.
  """
  return render_to_response('nodes/event_list.html',
    { 'events' : Event.objects.filter(node__owner = request.user).order_by('-timestamp', '-id')[0:30],
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
def package_list(request, node):
  """
  Display a list of node's installed packages.
  """
  node = get_object_or_404(Node, pk = node)
  if node.owner != request.user and not request.user.is_staff:
    raise Http404

  return render_to_response('nodes/installed_packages.html',
    { 'packages' : node.installedpackage_set.all().order_by('name'),
      'node'  : node },
    context_instance = RequestContext(request)
  )

