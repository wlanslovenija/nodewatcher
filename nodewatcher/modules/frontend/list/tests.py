import datetime
import json

from django.core import urlresolvers
from django.contrib.auth import models as auth_models
from django.utils import encoding, timezone

from tastypie import test

from guardian import shortcuts

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.modules.administration.location import models as location_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.administration.status import models as status_models
from nodewatcher.modules.administration.types import models as type_models

from . import resources

class NodeResourceTest(test.ResourceTestCase):
    api_name = 'v1'
    # To display full diff always.
    maxDiff = None

    def setUp(self):
        super(NodeResourceTest, self).setUp()

        self.node_list = self.resource_list_uri('node')

        self.projects = []
        for i in range(2):
            project = project_models.Project(
                name='Project name %s' % i,
                description='Project description %s' % i,
            )
            project.save()
            self.projects.append(project)

        self.users = []
        for i in range(3):
            user = auth_models.User.objects.create_user(
                username='username%s' % i,
            )
            user.save()
            self.users.append(user)

        self.types = list(type_models.TypeConfig._meta.get_field('type').get_registered_choices())
        self.monitoring_network = list(status_models.StatusMonitor._meta.get_field('network').get_registered_choices())
        self.monitoring_monitored = [True, False, None]
        self.monitoring_health = list(status_models.StatusMonitor._meta.get_field('health').get_registered_choices())

        self.initial_time = datetime.datetime(2014, 11, 5, 1, 5, 0, tzinfo=timezone.utc)

        self.nodes = []
        for i in range(45):
            node = core_models.Node()
            node.save()

            node.config.core.general(
                create=core_models.GeneralConfig,
                name='Node %s' % i,
            )

            maintainer = self.users[i % len(self.users)]
            shortcuts.assign_perm('change_node', maintainer, node)
            shortcuts.assign_perm('delete_node', maintainer, node)
            shortcuts.assign_perm('reset_node', maintainer, node)
            shortcuts.assign_perm('generate_firmware', maintainer, node)

            # Last seen / first seen
            node.monitoring.core.general(
                create=monitor_models.GeneralMonitor,
                first_seen=self.initial_time,
                last_seen=self.initial_time + datetime.timedelta(seconds=i),
            )

            # Status
            node.monitoring.core.status(
                create=status_models.StatusMonitor,
                network=self.monitoring_network[i % len(self.monitoring_network)].name,
                monitored=self.monitoring_monitored[i % len(self.monitoring_monitored)],
                health=self.monitoring_health[i % len(self.monitoring_health)].name,
            )

            # Type config
            type = self.types[i % len(self.types)]
            node.config.core.type(
                create=type_models.TypeConfig,
                type=type.name,
            )

            # Project config
            project = self.projects[i % len(self.projects)]
            node.config.core.project(
                create=project_models.ProjectConfig,
                project=project,
            )

            # Location config
            node.config.core.location(
                create=location_models.LocationConfig,
                address='Location %s' % i,
                city='Ljubljana',
                country='SI',
                timezone='Europe/Ljubljana',
                altitude=0,
                geolocation='POINT(%f %f)' % (10 + (i / 100.0), 40 + (i / 100.0)),
            )

            self.nodes.append(node)

    def resource_list_uri(self, resource_name):
        return urlresolvers.reverse('api:api_dispatch_list', kwargs={'api_name': self.api_name, 'resource_name': resource_name})

    def get_list(self, **kwargs):
        kwargs['format'] = 'json'

        response = self.api_client.get(self.node_list, data=kwargs)

        self.assertValidJSONResponse(response)

        return self.deserialize(response)

    def test_get_list_all(self):
        data = self.get_list(
            offset=0,
            limit=0,
        )

        nodes = data['objects']
        self.assertEqual(len(nodes), len(self.nodes))

        for i, json_node in enumerate(nodes):
            node = self.nodes[i]

            self.assertEqual(json_node, {
                u'status': {
                    u'health': node.monitoring.core.status().health,
                    u'monitored': node.monitoring.core.status().monitored,
                    u'network': node.monitoring.core.status().network,
                },
                u'uuid': encoding.force_unicode(node.uuid),
                u'name': node.config.core.general().name,
                u'project': node.config.core.project().project.name,
                u'location':  {
                    u'address': u'Location %s' % i,
                    u'altitude': 0.0,
                    u'city': u'Ljubljana',
                    u'country': u'SI',
                    u'geolocation': json.loads(node.config.core.location().geolocation.geojson),
                    u'timezone': u'Europe/Ljubljana',
                },
                # We manually construct URI to make sure it is like we assume it is.
                u'resource_uri': u'%s%s/' % (self.node_list, node.uuid),
                u'type': node.config.core.type().type,
                # Works correctly only if i < 60.
                u'last_seen': u'Wed, 05 Nov 2014 01:05:%02d +0000' % i,
            })

        self.assertEqual(data['meta'], {
            u'total_count': 45,
            # We specified 0 for limit in the request, so max limit should be used.
            u'limit': resources.NodeResource.Meta.max_limit,
            u'offset': 0,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': None,
        })
