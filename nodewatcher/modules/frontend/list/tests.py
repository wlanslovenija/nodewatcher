import datetime
import json
import uuid

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
    # To always display full diff.
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(NodeResourceTest, cls).setUpClass()

        cls.node_list = cls.resource_list_uri('node')

        cls.projects = []
        for i in range(2):
            project = project_models.Project(
                name='Project name %s' % i,
                description='Project description %s' % i,
            )
            project.save()
            cls.projects.append(project)

        cls.users = []
        for i in range(3):
            user = auth_models.User.objects.create_user(
                username='username%s' % i,
            )
            user.save()
            cls.users.append(user)

        # Registered choices are ordered based on their registration order.
        cls.types = [typ.name for typ in type_models.TypeConfig._meta.get_field('type').get_registered_choices()]
        cls.monitoring_network = [status.name for status in status_models.StatusMonitor._meta.get_field('network').get_registered_choices()]
        cls.monitoring_monitored = [True, False, None]
        cls.monitoring_health = [status.name for status in status_models.StatusMonitor._meta.get_field('health').get_registered_choices()]

        cls.initial_time = datetime.datetime(2014, 11, 5, 1, 5, 0, tzinfo=timezone.utc)

        cls.nodes = []
        for i in range(45):
            # We generate UUIDs so that they are nicely in sequence so that
            # default REST API ordering does not really change the order.
            node = core_models.Node(uuid=str(uuid.UUID(int=i, version=1)))
            node.save()

            node.config.core.general(
                create=core_models.GeneralConfig,
                name='Node %s' % i,
            )

            maintainer = cls.users[i % len(cls.users)]
            shortcuts.assign_perm('change_node', maintainer, node)
            shortcuts.assign_perm('delete_node', maintainer, node)
            shortcuts.assign_perm('reset_node', maintainer, node)
            shortcuts.assign_perm('generate_firmware', maintainer, node)

            # Last seen / first seen
            node.monitoring.core.general(
                create=monitor_models.GeneralMonitor,
                first_seen=cls.initial_time,
                last_seen=cls.initial_time + datetime.timedelta(seconds=i),
            )

            # Status
            node.monitoring.core.status(
                create=status_models.StatusMonitor,
                network=cls.monitoring_network[i % len(cls.monitoring_network)],
                monitored=cls.monitoring_monitored[i % len(cls.monitoring_monitored)],
                health=cls.monitoring_health[i % len(cls.monitoring_health)],
            )

            # Type config
            node.config.core.type(
                create=type_models.TypeConfig,
                type=cls.types[i % len(cls.types)],
            )

            # Project config
            node.config.core.project(
                create=project_models.ProjectConfig,
                project=cls.projects[i % len(cls.projects)],
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

            cls.nodes.append(node)

        # By default we have nodes ordered by UUID in the REST API.
        sorted_nodes = sorted(cls.nodes, key=lambda node: node.uuid)

        # But it should not really change the ordering, because we are generating UUIDs in sequence.
        assert [node.uuid for node in sorted_nodes] == [node.uuid for node in cls.nodes]

    @classmethod
    def resource_list_uri(cls, resource_name):
        return urlresolvers.reverse('api:api_dispatch_list', kwargs={'api_name': cls.api_name, 'resource_name': resource_name})

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

    def test_get_list_offset(self):
        data = self.get_list(
            offset=11,
            limit=0,
        )

        nodes = data['objects']
        self.assertEqual([node['uuid'] for node in nodes], [node.uuid for node in self.nodes[11:]])

        self.assertEqual(data['meta'], {
            u'total_count': 45,
            # We specified 0 for limit in the request, so max limit should be used.
            u'limit': resources.NodeResource.Meta.max_limit,
            u'offset': 11,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': None,
        })

    def test_get_list_page(self):
        data = self.get_list(
            offset=6,
            limit=20,
        )

        nodes = data['objects']
        self.assertEqual([node['uuid'] for node in nodes], [node.uuid for node in self.nodes[6:26]])

        self.assertEqual(data['meta'], {
            u'total_count': 45,
            u'limit': 20,
            u'offset': 6,
            u'nonfiltered_count': 45,
            u'next': u'%s?format=json&limit=20&offset=26' % self.node_list,
            u'previous': None,
        })

    def test_get_list_last_page(self):
        data = self.get_list(
            offset=40,
            limit=20,
        )

        nodes = data['objects']
        self.assertEqual([node['uuid'] for node in nodes], [node.uuid for node in self.nodes[40:]])

        self.assertEqual(data['meta'], {
            u'total_count': 45,
            u'limit': 20,
            u'offset': 40,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': u'%s?format=json&limit=20&offset=20' % self.node_list,
        })

    def test_ordering(self):
        for offset in (0, 4):
            for limit in (0, 20):
                for reverse in (False, True):
                    for ordering, key in (
                        ('name', lambda node: node.config.core.general().name),
                        ('type', lambda node: self.types.index(node.config.core.type().type)),
                        ('project', lambda node: node.config.core.project().project.name),
                        #('location__geolocation', lambda node: node.config.core.location().geolocation),
                        ('last_seen', lambda node: node.monitoring.core.general().last_seen),
                        #('status__health', lambda node: self.monitoring_health.index(node.monitoring.core.status().health)),
                        #('status__monitored', lambda node: self.monitoring_monitored.index(node.monitoring.core.status().monitored)),
                        #('status__network', lambda node: self.monitoring_network.index(node.monitoring.core.status().network)),
                    ):
                        ordering = '%s%s' % ('-' if reverse else '', ordering)
                        data = self.get_list(
                            offset=offset,
                            limit=limit,
                            order_by=ordering
                        )

                        nodes = data['objects']
                        self.assertEqual([node['uuid'] for node in nodes], [node.uuid for node in sorted(self.nodes, key=key, reverse=reverse)[offset:offset + limit if limit else None]], 'offset=%s, limit=%s, ordering=%s' % (offset, limit, ordering))

                        self.assertEqual(data['meta'], {
                            u'total_count': 45,
                            u'limit': limit or resources.NodeResource.Meta.max_limit,
                            u'offset': offset,
                            u'nonfiltered_count': 45,
                            u'next': u'%s?order_by=%s&format=json&limit=%s&offset=%s' % (self.node_list, ordering, limit, offset + limit) if limit else None,
                            u'previous': None,
                        })

    def test_ordering_multiple(self):
        for offset in (0, 4):
            for limit in (0, 20):
                ordering = ['type', 'name']
                data = self.get_list(
                    offset=offset,
                    limit=limit,
                    order_by=ordering
                )

                key = lambda node: (self.types.index(node.config.core.type().type), node.config.core.general().name)

                nodes = data['objects']
                self.assertEqual([node['uuid'] for node in nodes], [node.uuid for node in sorted(self.nodes, key=key)[offset:offset + limit if limit else None]], 'offset=%s, limit=%s, ordering=%s' % (offset, limit, ordering))

                self.assertEqual(data['meta'], {
                    u'total_count': 45,
                    u'limit': limit or resources.NodeResource.Meta.max_limit,
                    u'offset': offset,
                    u'nonfiltered_count': 45,
                    u'next': u'%s?order_by=type&order_by=name&format=json&limit=%s&offset=%s' % (self.node_list, limit, offset + limit) if limit else None,
                    u'previous': None,
                })
