from django.db import models


class NodeChannel(models.Model):
    node_interface = models.CharField(max_length=20)
    node_channel = models.IntegerField()
