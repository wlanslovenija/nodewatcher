from django.db import models
from django.contrib.auth.models import User

class Zone(models.Model):
  zone = models.CharField(max_length = 255, primary_key = True)
  owner = models.ForeignKey(User)
  active = models.BooleanField()

  primary_ns = models.CharField(max_length = 255)
  resp_person = models.CharField(max_length = 255)
  serial = models.IntegerField()
  refresh = models.IntegerField()
  retry = models.IntegerField()
  expire = models.IntegerField()
  minimum = models.IntegerField()

class Record(models.Model):
  zone = models.ForeignKey(Zone)
  name = models.CharField(max_length = 255)
  ttl = models.IntegerField()
  type = models.CharField(max_length = 255)
  data = models.CharField(max_length = 255)
  mx_priority = models.IntegerField(default = 0)

  @staticmethod
  def for_node(node, zone = None, name = None):
    """
    Returns a Record instance for a given node (or creates a new instance
    if there is none yet).
    
    @param node: A valid Node instance
    """
    if not name:
      name = node.name
    if not zone:
      zone = node.project.zone

    try:
      record = Record.objects.get(zone = zone, name = "%s.nodes" % name)
    except Record.DoesNotExist:
      record = Record()

    return record

  @staticmethod
  def remove_for_node(node):
    """
    Removes DNS records for a given node.

    @param node: A valid Node instance
    """
    if node.is_invalid():
      return
    
    record = Record.for_node(node)
    if record.id:
      record.delete()

  @staticmethod
  def update_for_node(node, old_name = None, old_project = None):
    """
    Updates DNS records for a given node.
  
    @param node: A valid Node instance
    @param old_name: Old node name
    @param old_project: Old node project
    """
    if node.is_invalid():
      return
    
    old_zone = old_project.zone if old_project else None

    # Update A record
    record = Record.for_node(node, name = old_name, zone = old_zone)
    
    if not node.project.zone:
      if record.id:
        record.delete()
    else:
      record.zone = node.project.zone
      record.name = "%s.nodes" % node.name
      record.ttl = 3600
      record.type = "A"
      record.data = node.ip
      record.save()

    # Update the zones
    if old_zone and old_zone != record.zone:
      old_zone.serial += 1
      old_zone.save()
    
    try:
      record.zone.serial += 1
      record.zone.save()
    except Zone.DoesNotExist:
      pass

