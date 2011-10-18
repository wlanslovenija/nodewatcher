from datetime import datetime
import os.path

from django.conf import settings
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.db import models, transaction
from django.forms import forms
from django.utils.translation import ugettext as _
from django.core import context_processors as core_context_processors
from django.core.urlresolvers import reverse

from web.account import decorators as account_decorators
from web.account.utils import generate_random_password, initial_accepts_request
from web.nodes import ipcalc
from web.nodes import context_processors as nodes_context_processors
from web.nodes import decorators
from web.nodes.forms import RegisterNodeForm, UpdateNodeForm, AllocateSubnetForm, WhitelistMacForm, EventSubscribeForm, RenumberForm, RenumberAction, EditSubnetForm
from web.nodes.common import ValidationWarning
from web.nodes.util import queryset_by_ip
from web.generator.models import Profile
from web.policy.models import Policy, PolicyFamily, TrafficControlClass
from web.nodes.models import Node, NodeType, NodeStatus, Subnet, SubnetStatus, APClient, Pool, WhitelistItem, Link, Event, EventSubscription, SubscriptionType, Project, EventCode, EventSource, GraphItemNP, GraphType, PoolStatus

def nodes(request):
  """
  Display a list of all current nodes and their status.
  """
  return render_to_response('nodes/list.html',
    { 'nodes' : queryset_by_ip(Node.objects.all(), 'ip', 'node_type') },
    context_instance = RequestContext(request)
  )

def pools(request):
  """
  Displays IP allocation pools.
  """
  return render_to_response('nodes/pools.html',
    { 'pools' : queryset_by_ip(Pool.objects.filter(parent = None), 'ip_subnet') },
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
  for s in Node.objects.exclude(node_type__in = (NodeType.Test, NodeType.Dead)).order_by('status').values('status').annotate(count = models.Count('ip')):
    nodes_by_status.append({ 'status' : NodeStatus.as_string(s['status']), 'count' : s['count'] })

  # Nodes by template usage
  others = Node.objects.exclude(node_type__in = (NodeType.Test, NodeType.Dead)).count()
  templates_by_usage = []
  for t in Profile.objects.exclude(node__node_type__in = (NodeType.Test, NodeType.Dead)).values('template__name').annotate(count = models.Count('node')).order_by('template__name'):
    templates_by_usage.append({ 'template' : t['template__name'], 'count' : t['count'] })
    others -= t['count']
  
  if others > 0:
    templates_by_usage.append({ 'template' : _("unknown"), 'count' : others, 'special' : True })

  # Nodes by project
  all_nodes = Node.objects.exclude(node_type__in = (NodeType.Test, NodeType.Dead)).values('project__name', 'project__pk').annotate(count = models.Count('ip'))
  up_nodes = all_nodes.filter(status = NodeStatus.Up)
  nodes_by_project = []
  others = 0
  for p in all_nodes.order_by('project__id'):
    if not p['project__name']:
      others = p['count']
    else:
      try:
        up_count = filter(lambda x: x['project__pk'] == p['project__pk'], up_nodes)[0]['count']
      except IndexError:
        up_count = 0
      
      nodes_by_project.append({ 'name' : p['project__name'], 'count' : p['count'], 'up_count' : up_count})
  
  if others > 0:
    nodes_by_project.append({ 'name' : _("unknown"), 'count' : others, 'special' : True})

  # XXX These graphs are currently hardcoded and should be removed on graph API refactor
  graphs = [
    GraphItemNP.static(-1, GraphType.NodesByStatus, "global_nodes_by_status.png", "Nodes By Status"),
    GraphItemNP.static(-2, GraphType.Clients, "global_client_count.png", "Global Client Count")
  ]

  peers_avg = Node.objects.filter(peers__gt = 0).aggregate(num = models.Avg('peers'))['num']

  return render_to_response('nodes/statistics.html',
    { 'node_count' : node_count,
      'nodes_by_status' : nodes_by_status,
      'nodes_by_project' : nodes_by_project,
      'nodes_warned' : Node.objects.filter(warnings = True).exclude(node_type__in = (NodeType.Test, NodeType.Dead)).count(),
      'nodes_test' : Node.objects.filter(node_type = NodeType.Test).count(),
      'nodes_dead' : Node.objects.filter(node_type = NodeType.Dead).count(),
      'subnet_count' : Subnet.objects.all().count(),
      'clients_online' : APClient.objects.all().count(),
      'clients_ever' : Node.objects.aggregate(num = models.Sum('clients_so_far'))['num'] or 0,
      'external_ant' : Node.objects.filter(ant_external = True).exclude(node_type__in = (NodeType.Test, NodeType.Dead)).count(),
      'template_usage' : templates_by_usage,
      'peers_avg' : 0 if peers_avg is None else round(peers_avg, 2),
      'graphs' : graphs,
      'timespans' : settings.GRAPH_TIMESPAN_PREFIXES
    },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def my_nodes(request):
  """
  Display a list of current user's nodes.
  """
  return render_to_response('nodes/my.html',
    { 'nodes' : queryset_by_ip(request.user.node_set.all(), 'ip', 'node_type') },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def node_new(request):
  """
  Display a form for registering a new node.
  """
  if request.method == 'POST':
    form = initial_accepts_request(request, RegisterNodeForm)(request.POST)
    if form.is_valid() and form.save(request.user):
      return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': form.node.get_current_id() }))
  else:
    form = initial_accepts_request(request, RegisterNodeForm)()

  return render_to_response('nodes/new.html',
    { 'form' : form,
      'mobile_node_type' : NodeType.Mobile,
      'dead_node_type' : NodeType.Dead,
      'nonstaff_border_routers' : getattr(settings, 'NONSTAFF_BORDER_ROUTERS', False),
      'projects' : Project.objects.all().order_by("id") },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_edit(request, node):
  """
  Display a form for registering a new node.
  """
  if not node.is_current_owner(request):
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
        return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))
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
      'vpn_server'          : node.vpn_server,
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
        'wan_dhcp'            : True,
        'wan_ip'              : '',
        'wan_gw'              : '',
        'root_pass'           : generate_random_password(8),
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
      'dead_node_type' : NodeType.Dead,
      'nonstaff_border_routers' : getattr(settings, 'NONSTAFF_BORDER_ROUTERS', False),
      'projects' : Project.objects.all().order_by("id") },
    context_instance = RequestContext(request)
  )

@decorators.node_argument(be_robust=True)
def node(request, node):
  """
  Displays node info.
  """
  # Queue requests to redraw all graphs
  node.redraw_graphs()
  
  return render_to_response('nodes/node.html',
    { 'node' : node ,
      'timespans' : settings.GRAPH_TIMESPAN_PREFIXES,
      'current_owner' : node.is_current_owner(request) },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_reset(request, node):
  """
  Displays a form where the user can confirm node data reset. If
  confirmed, node data is reset and node is moved into pending
  state.
  """
  if not node.is_current_owner(request):
    raise Http404

  if request.method == 'POST':
    # Reset confirmed
    if node.is_resettable():
      node.status = NodeStatus.Pending
      node.reset()
      node.save()

      return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))

  return render_to_response('nodes/reset.html',
    { 'node' : node },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_remove(request, node):
  """
  Displays node info.
  """
  if not node.is_current_owner(request):
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

@account_decorators.authenticated_required
@decorators.node_argument
def node_renumber(request, node):
  """
  Renumbers a given node.
  """
  if not node.is_current_owner(request):
    raise Http404
  
  if request.method == 'POST':
    form = RenumberForm(request.user, node, request.POST)
    try:
      sid = transaction.savepoint()
      if form.is_valid():
        form.save()
        transaction.savepoint_commit(sid)
        return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))
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
      'form' : form },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_allocate_subnet(request, node):
  """
  Displays node info.
  """
  if not node.is_current_owner(request):
    raise Http404
 
  if request.method == 'POST':
    form = AllocateSubnetForm(node, request.POST)
    if form.is_valid() and form.save(node):
      return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))
  else:
    form = AllocateSubnetForm(node)

  return render_to_response('nodes/allocate_subnet.html',
    { 'form' : form,
      'node' : node },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_deallocate_subnet(request, node, subnet_id):
  """
  Removes a subnet.
  """
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  if node.pk != subnet.node.pk:
    raise Http404
  if not node.is_current_owner(request):
    raise Http404
  
  if request.method == 'POST':
    if subnet.is_primary():
      raise Http404

    subnet.delete()
    return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))

  return render_to_response('nodes/deallocate_subnet.html',
    { 'node' : node,
      'subnet' : subnet },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
@decorators.node_argument
def node_edit_subnet(request, node, subnet_id):
  """
  Edits a subnet.
  """
  subnet = get_object_or_404(Subnet, pk = subnet_id)
  if node.pk != subnet.node.pk:
    raise Http404
  if not node.is_current_owner(request):
    raise Http404
  
  if request.method == 'POST':
    form = EditSubnetForm(node, request.POST)
    if form.is_valid() and form.save(subnet):
      return HttpResponseRedirect(reverse("view_node", kwargs={ 'node': node.get_current_id() }))
    else:
      subnet = Subnet.objects.get(pk = subnet_id)
  else:
    form = EditSubnetForm(node, initial = {
      'description' : subnet.description,
      'dhcp' : subnet.gen_dhcp
    })

  return render_to_response('nodes/edit_subnet.html',
    { 'node'   : node,
      'subnet' : subnet,
      'form'   : form },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def whitelisted_mac(request):
  """
  Display a form for whitelisting a MAC address.
  """
  if request.method == 'POST':
    form = WhitelistMacForm(request.POST)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect(reverse('my_whitelist'))
  else:
    form = WhitelistMacForm()

  whitelist = request.user.whitelistitem_set.order_by('mac')
  return render_to_response('nodes/whitelisted_mac.html',
    { 'form' : form,
      'whitelist' : whitelist },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def unwhitelist_mac(request, item_id):
  """
  Removes a whitelisted MAC address.
  """
  item = get_object_or_404(WhitelistItem, pk = item_id)
  if item.owner != request.user and not request.user.is_staff:
    raise Http404
  
  item.delete()
  return HttpResponseRedirect(reverse('my_whitelist'))

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
  Displays network topology.
  """
  return render_to_response('nodes/topology.html', {},
    context_instance = RequestContext(request)
  )

def map(request):
  """
  Displays network map.
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
  clients = APClient.objects.all().order_by('node__name', 'connected_at')
  return render_to_response('nodes/gcl.html',
    { 'clients' : clients },
    context_instance = RequestContext(request)
  )

def global_events(request):
  """
  Display a list of global network events.
  """
  return render_to_response('nodes/global_events.html',
    { 'events' : Event.objects.all().order_by('-timestamp', '-id')[0:30] },
    context_instance = RequestContext(request)
  )

@decorators.node_argument(be_robust=True)
def node_events(request, node):
  """
  Display a list of a node's events.
  """
  return render_to_response('nodes/node_events.html',
    { 'node' : node,
      'events' : node.event_set.order_by('-timestamp', '-id')[0:30] },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def event_list(request):
  """
  Display a list of current user's events.
  """
  return render_to_response('nodes/event_list.html',
    { 'events' : Event.objects.filter(node__owner = request.user).order_by('-timestamp', '-id')[0:30],
      'subscriptions' : EventSubscription.objects.filter(user = request.user) },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def event_subscribe(request):
  """
  Display a form for subscribing to an event.
  """
  if request.method == 'POST':
    form = EventSubscribeForm(request.POST, request=request)
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect(reverse('my_events'))
  else:
    form = EventSubscribeForm()

  return render_to_response('nodes/event_subscribe.html',
    { 'form' : form,
      'single_node_type' : SubscriptionType.SingleNode },
    context_instance = RequestContext(request)
  )

@account_decorators.authenticated_required
def event_unsubscribe(request, subscription_id):
  """
  Removes event subscription.
  """
  s = get_object_or_404(EventSubscription, pk = subscription_id)
  if s.user != request.user and not request.user.is_staff:
    raise Http404
  
  s.delete()

  return HttpResponseRedirect(reverse('my_events'))

@account_decorators.authenticated_required
@decorators.node_argument
def package_list(request, node):
  """
  Display a list of node's installed packages.
  """
  if not node.is_current_owner(request):
    raise Http404

  return render_to_response('nodes/installed_packages.html',
    { 'packages' : node.installedpackage_set.all().order_by('name'),
      'node'  : node },
    context_instance = RequestContext(request)
  )

def forbidden_view(request, reason=""):
  """
  Displays 403 fobidden page. For example, when request fails CSRF protection.
  """

  from django.middleware.csrf import REASON_NO_REFERER
  t = loader.get_template("403.html")
  return HttpResponseForbidden(t.render(RequestContext(request, {
      'DEBUG'  : settings.DEBUG,
      'reason' : reason,
      'no_referer' : reason == REASON_NO_REFERER,
    })))
