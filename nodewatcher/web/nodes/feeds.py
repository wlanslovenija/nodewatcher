from django.contrib.syndication.views import Feed
from django.contrib.gis.feeds import Feed as GeoFeed
from django.contrib.auth.models import User
from django.conf import settings
from web.nodes.models import Event, Node, NodeType, NodeStatus
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

class LatestEvents(Feed):
  base_link = "%s://%s" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
  author_name = settings.NETWORK_NAME
  author_link = "%s/" % base_link
  title_template = "feeds/events_title.html"
  description_template = "feeds/events_description.html"
  
  def get_object(self, request, username=None):
    if 'lite' in request.GET:
      # I would call this a small hack
      self.description_template = "feeds/events_lite.html"
    else:
      self.description_template = "feeds/events_description.html"

    if not username:
      return None
    else:
      return get_object_or_404(User, username=username)
  
  def title(self, obj):
    if obj:
      return u"%s \u2013 Latest network events for %s" % (settings.NETWORK_NAME, obj.username)
    else:
      return u"%s \u2013 Latest network events" % settings.NETWORK_NAME
  
  def link(self):
    # Users do not have special events page so we link both feeds to global events
    return "%s%s" % (self.base_link, reverse('network_events'))
  
  def description(self, obj):
    if obj:
       return "Latest events generated by nodes maintained by %s." % obj.username
    else:
       return "Latest events generated by nodes in the network."
  
  def items(self, obj):
    if obj:
      return Event.objects.filter(node__owner=obj).order_by('-timestamp')[:30]
    else:
      return Event.objects.order_by('-timestamp')[:30]
  
  def item_pubdate(self, item):
    return item.timestamp

  def item_guid(self, item):
    return "%s-event-%s" % (item.node.pk, item.pk)
  
  def item_link(self, item):
    return "%s%s" % (self.base_link, reverse('view_node_events', kwargs={'node': item.node.get_current_id()}))

class ActiveNodes(GeoFeed):
  base_link = "%s://%s" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
  description = "Currently active nodes in the network."
  
  def title(self):
    return u"%s \u2013 Active nodes" % settings.NETWORK_NAME
  
  def link(self):
    return "%s%s" % (self.base_link, reverse('nodes_list'))
  
  def items(self):
    return Node.objects.filter(node_type = NodeType.Mesh).filter(status = NodeStatus.Up).exclude(geo_lat = None).exclude(geo_long = None)

  def item_pubdate(self, item):
    return item.last_seen
  
  def item_guid(self, item):
    return item.pk
  
  def item_geometry(self, item):
    return (item.geo_long, item.geo_lat)
  
  def item_link(self, item):
    return item.get_full_url(getattr(settings, 'FEEDS_USE_HTTPS', None))
