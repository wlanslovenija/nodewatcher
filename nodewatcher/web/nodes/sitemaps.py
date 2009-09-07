from django.contrib.sitemaps import Sitemap
from wlanlj.nodes.models import Node
from datetime import datetime

class NodeSitemap(Sitemap):
  changefreq = "daily"

  def items(self):
    return Node.objects.all()

  def lastmod(self, node):
    return node.last_seen

  def location(self, node):
    return "/nodes/node/%s" % node.ip

class StaticSitemap(Sitemap):
  changefreq = "daily"
  locations = [
    '/nodes/statistics',
    '/nodes/topology',
    '/nodes/map',
    '/'
  ]

  def items(self):
    return self.locations

  def lastmod(self, obj):
    return datetime.now()

  def location(self, obj):
    return obj

