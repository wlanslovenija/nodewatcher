from django.db import models

from web.nodes import models as node_models

class RegistryItem(models.Model):
  node = models.ForeignKey(node_models.Node, null = True)
  
  class Meta:
    abstract = True
  
class HardwareConfig(RegistryItem):
  model = models.CharField(max_length = 20) # TODO fkey to models
  
  class RegistryMeta:
    form_order = 1
    path = "core.hardware"

