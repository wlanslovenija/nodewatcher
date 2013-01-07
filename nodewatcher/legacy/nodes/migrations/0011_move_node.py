# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('core', '0037_move_project'),
        ('cgm', '0036_remove_antenna_field'),
        ('monitor', '0001_initial'),
        ('projects', '0002_initial_p2'),
        ('antennas', '0002_transfer_data'),
    )

    def forwards(self, orm):
        db.rename_table('nodes_node', 'core_node')


    def backwards(self, orm):
        db.rename_table('core_node', 'nodes_node')


    models = {
        
    }

    complete_apps = ['nodes']