from django.contrib.sitemaps import Sitemap
from web.nodes.models import Node
from datetime import datetime
import re
from django.conf import settings

class HttpsSitemap(Sitemap):
  http_match = re.compile(r"^http://")

  def get_urls(self, page=1):
    urls = super(HttpsSitemap, self).get_urls(page)
    if getattr(settings, 'SITEMAPS_USE_HTTPS', None):
      for url in urls:
        url['location'] = self.http_match.sub("https://", url['location'])
    return urls

class NodeSitemap(HttpsSitemap):
  priority = "0.8"

  def items(self):
    return Node.objects.all()

  def lastmod(self, node):
    return node.last_seen

  def location(self, node):
    return node.get_absolute_url()

class StaticSitemap(HttpsSitemap):
  priority = "0.9"
  locations = [
    '/nodes/statistics',
    '/nodes/topology',
    '/nodes/map'
  ]

  def items(self):
    return self.locations

  def lastmod(self, obj):
    return datetime.now()

  def location(self, obj):
    return obj

class RootPageSitemap(StaticSitemap):
  priority = "1.0"
  locations = [
    '/'
  ]

  def items(self):
    return self.locations

  def lastmod(self, obj):
    return datetime.now()

  def location(self, obj):
    return obj
