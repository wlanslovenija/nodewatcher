import uuid

from django.db import models

class Project(models.Model):
  """
  This class represents a project. Each project can contains some
  nodes and is also assigned a default IP allocation pool.
  """
  name = models.CharField(max_length = 50)
  description = models.CharField(max_length = 200)
  channel = models.IntegerField()
  ssid = models.CharField(max_length = 50)
  ssid_backbone = models.CharField(max_length = 50)
  ssid_mobile = models.CharField(max_length = 50)
  captive_portal = models.BooleanField()
  sticker = models.CharField(max_length = 50)
  
  # Geographical location
  geo_lat = models.FloatField(null = True)
  geo_long = models.FloatField(null = True)
  geo_zoom = models.IntegerField(null = True)

  def __unicode__(self):
    """
    Returns this project's name.
    """
    return self.name

def project_default(request=None):
  if request and hasattr(request.user, 'get_profile'):
    return request.user.get_profile().default_project
  else:
    projects = Project.objects.all()
    if projects.exists():
      return projects[0]
    else:
      return None

class Node(models.Model):
  """
  This class represents a single node in the network.
  """
  uuid = models.CharField(max_length = 40, primary_key = True)  

  def save(self, **kwargs):
    """
    Override save so we can generate UUIDs.
    """
    if not self.uuid:
      self.pk = str(uuid.uuid4())
    
    super(Node, self).save(**kwargs)
  
  def __unicode__(self):
    """
    Returns a string representation of this node.
    """
    return self.uuid
