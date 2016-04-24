import datetime
import json
import os
import unittest
import urllib
import uuid

from django.apps import apps
from django.contrib.auth import models as auth_models
from django.utils import encoding, timezone

from guardian import shortcuts

from django_datastream import test_runner

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.modules.administration.location import models as location_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.administration.status import models as status_models
from nodewatcher.modules.administration.types import models as type_models

from . import resources


class NodeResourceTest(test_runner.ResourceTestCase):
    namespace = 'api'

    @classmethod
    def setUpClass(cls):
        super(NodeResourceTest, cls).setUpClass()

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
        cls.monitoring_network = [status.name for status in status_models.StatusMonitor._meta.get_field('network').get_registered_choices()] + [None]
        cls.monitoring_monitored = [True, False, None]
        cls.monitoring_health = [status.name for status in status_models.StatusMonitor._meta.get_field('health').get_registered_choices()] + [None]

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
                defaults={
                    'geolocation': 'POINT(%f %f)' % (10 + (i / 100.0), 40 + (i / 100.0)),
                }
            )

            cls.nodes.append(node)

        # By default we have nodes ordered by UUID in the REST API.
        sorted_nodes = sorted(cls.nodes, key=lambda node: node.uuid)

        # But it should not really change the ordering, because we are generating UUIDs in sequence.
        assert [node.uuid for node in sorted_nodes] == [node.uuid for node in cls.nodes]

    def assertNodeEqual(self, i, node, json_node, selection=lambda node: node):
        self.assertEqual(selection({
            u'status': {
                u'health': node.monitoring.core.status().health,
                u'monitored': node.monitoring.core.status().monitored,
                u'network': node.monitoring.core.status().network,
            },
            u'uuid': encoding.force_unicode(node.uuid),
            u'name': node.config.core.general().name,
            u'project': node.config.core.project().project.name,
            u'location': {
                u'address': u'Location %s' % i,
                u'altitude': 0.0,
                u'city': u'Ljubljana',
                u'country': u'SI',
                u'geolocation': json.loads(node.config.core.location().geolocation.geojson),
                u'timezone': u'Europe/Ljubljana',
            },
            u'router_id': [],
            u'routing_topology': [],
            # We manually construct URI to make sure it is like we assume it is.
            u'resource_uri': u'%s%s/' % (self.resource_list_uri('node'), node.uuid),
            u'type': node.config.core.type().type,
            # Works correctly only if i < 60.
            u'last_seen': u'2014-11-05T01:05:%02dZ' % i,
        }), json_node)

    def project(self, source, projection):
        # Based on https://gist.github.com/bauman/2f68cebfddf9dc9c763a

        # resource_uri is always included.
        projection['resource_uri'] = 1

        result = {}
        for key in projection:
            path = key.split('.')
            path_length = len(path)
            source_pointer = source
            result_pointer = result
            for level in range(path_length):
                if level == path_length - 1:
                    if path[level] in source_pointer:
                        result_pointer[path[level]] = source_pointer[path[level]]
                    else:
                        result_pointer[path[level]] = None
                else:
                    if path[level] not in result_pointer:
                        result_pointer[path[level]] = {}
                    result_pointer = result_pointer[path[level]]
                    source_pointer = source_pointer[path[level]]
        return result

    def test_api_uris(self):
        # URIs have to be stable.

        self.assertEqual('/api/v1/node/', self.resource_list_uri('node'))
        self.assertEqual('/api/v1/node/schema/', self.resource_schema_uri('node'))

    def test_read_only(self):
        node_uri = '%s%s/' % (self.resource_list_uri('node'), self.nodes[0].uuid)

        self.assertHttpMethodNotAllowed(self.api_client.post(self.resource_list_uri('node'), format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.put(node_uri, format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.patch(node_uri, format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.delete(node_uri, format='json'))

    def test_get_list_all(self):
        data = self.get_list(
            'node',
            offset=0,
            limit=0,
        )

        nodes = data['objects']
        self.assertEqual(len(self.nodes), len(nodes))

        for i, json_node in enumerate(nodes):
            node = self.nodes[i]
            self.assertNodeEqual(i, node, json_node)

        self.assertEqual({
            u'total_count': 45,
            # We specified 0 for limit in the request, so max limit should be used.
            u'limit': resources.NodeResource._meta.max_limit,
            u'offset': 0,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': None,
        }, data['meta'])

    def test_get_list_offset(self):
        data = self.get_list(
            'node',
            offset=11,
            limit=0,
        )

        nodes = data['objects']
        self.assertEqual([node.uuid for node in self.nodes[11:]], [node['uuid'] for node in nodes])

        self.assertMetaEqual({
            u'total_count': 45,
            # We specified 0 for limit in the request, so max limit should be used.
            u'limit': resources.NodeResource._meta.max_limit,
            u'offset': 11,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': u'%s?format=json&limit=11&offset=0' % self.resource_list_uri('node'),
        }, data['meta'])

    def test_get_list_page(self):
        data = self.get_list(
            'node',
            offset=6,
            limit=20,
        )

        nodes = data['objects']
        self.assertEqual([node.uuid for node in self.nodes[6:26]], [node['uuid'] for node in nodes])

        self.assertMetaEqual({
            u'total_count': 45,
            u'limit': 20,
            u'offset': 6,
            u'nonfiltered_count': 45,
            u'next': u'%s?format=json&limit=20&offset=26' % self.resource_list_uri('node'),
            u'previous': u'%s?format=json&limit=6&offset=0' % self.resource_list_uri('node'),
        }, data['meta'])

    def test_get_list_last_page(self):
        data = self.get_list(
            'node',
            offset=40,
            limit=20,
        )

        nodes = data['objects']
        self.assertEqual([node.uuid for node in self.nodes[40:]], [node['uuid'] for node in nodes])

        self.assertMetaEqual({
            u'total_count': 45,
            u'limit': 20,
            u'offset': 40,
            u'nonfiltered_count': 45,
            u'next': None,
            u'previous': u'%s?format=json&limit=20&offset=20' % self.resource_list_uri('node'),
        }, data['meta'])

    def test_ordering(self):
        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                for reverse in (False, True):
                    for ordering, key in (
                        ('name', lambda node: node.config.core.general().name),
                        ('type', lambda node: self.types.index(node.config.core.type().type)),
                        ('project', lambda node: node.config.core.project().project.name),
                        ('last_seen', lambda node: node.monitoring.core.general().last_seen),
                        ('status__health', lambda node: self.monitoring_health.index(node.monitoring.core.status().health)),
                        ('status__monitored', lambda node: self.monitoring_monitored.index(node.monitoring.core.status().monitored)),
                        ('status__network', lambda node: self.monitoring_network.index(node.monitoring.core.status().network)),
                    ):
                        ordering = '%s%s' % ('-' if reverse else '', ordering)
                        data = self.get_list(
                            'node',
                            offset=offset,
                            limit=limit,
                            order_by=ordering,
                        )

                        nodes = data['objects']
                        self.assertEqual([node.uuid for node in sorted(self.nodes, key=key, reverse=reverse)[offset:offset + limit if limit else None]], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, ordering=%s' % (offset, limit, ordering))

                        limit = limit or resources.NodeResource._meta.max_limit

                        if 0 < offset < limit:
                            previous_limit = offset
                        else:
                            previous_limit = limit

                        self.assertMetaEqual({
                            u'total_count': 45,
                            u'limit': limit,
                            u'offset': offset,
                            u'nonfiltered_count': 45,
                            u'next': u'%s?order_by=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(ordering), limit, offset + limit) if limit and len(self.nodes) > offset + limit else None,
                            u'previous': u'%s?order_by=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(ordering), previous_limit, offset - previous_limit) if offset != 0 else None,
                        }, data['meta'])

    def test_ordering_multiple(self):
        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                ordering = ['type', 'name']
                data = self.get_list(
                    'node',
                    offset=offset,
                    limit=limit,
                    order_by=ordering,
                )

                key = lambda node: (self.types.index(node.config.core.type().type), node.config.core.general().name)

                nodes = data['objects']
                self.assertEqual([node.uuid for node in sorted(self.nodes, key=key)[offset:offset + limit if limit else None]], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, ordering=%s' % (offset, limit, ordering))

                limit = limit or resources.NodeResource._meta.max_limit

                if 0 < offset < limit:
                    previous_limit = offset
                else:
                    previous_limit = limit

                self.assertMetaEqual({
                    u'total_count': 45,
                    u'limit': limit,
                    u'offset': offset,
                    u'nonfiltered_count': 45,
                    u'next': u'%s?order_by=type&order_by=name&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), limit, offset + limit) if limit and len(self.nodes) > offset + limit else None,
                    u'previous': u'%s?order_by=type&order_by=name&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), previous_limit, offset - previous_limit) if offset != 0 else None,
                }, data['meta'])

    def test_global_filter(self):
        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                for global_filter, filter_function in (
                    ('project name 0', lambda node: node.config.core.project().project.name == 'Project name 0'),
                    ('wireless', lambda node: node.config.core.type().type == 'wireless'),
                    ('node 5', lambda node: node.config.core.general().name == 'Node 5'),
                    ('Project NAME 0', lambda node: node.config.core.project().project.name == 'Project name 0'),
                    ('wireLess', lambda node: node.config.core.type().type == 'wireless'),
                    ('nODe 5', lambda node: node.config.core.general().name == 'Node 5'),
                    ('ProjecT', lambda node: True), # All nodes are in projects.
                ):
                    data = self.get_list(
                        'node',
                        offset=offset,
                        limit=limit,
                        filter=global_filter,
                    )

                    filtered_nodes = [node.uuid for node in filter(filter_function, self.nodes)]
                    nodes = data['objects']
                    self.assertEqual(filtered_nodes[offset:offset + limit if limit else None], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, filter=%s' % (offset, limit, global_filter))

                    limit = limit or resources.NodeResource._meta.max_limit

                    if 0 < offset < limit:
                        previous_limit = offset
                    else:
                        previous_limit = limit

                    self.assertMetaEqual({
                        u'total_count': len(filtered_nodes),
                        u'limit': limit,
                        u'offset': offset,
                        u'nonfiltered_count': 45,
                        u'next': u'%s?filter=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(global_filter), limit, offset + limit) if limit and len(filtered_nodes) > offset + limit else None,
                        u'previous': u'%s?filter=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(global_filter), previous_limit, offset - previous_limit) if offset != 0 else None,
                    }, data['meta'])

    def test_field_filters(self):
        health_filter = [str(h) for h in self.monitoring_health[0:2]]

        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                for field_filter, filter_function in (
                    ({'project': 'Project name 0'}, lambda node: node.config.core.project().project.name == 'Project name 0'),
                    ({'type': 'wireless'}, lambda node: node.config.core.type().type == 'wireless'),
                    ({'name': 'Node 5'}, lambda node: node.config.core.general().name == 'Node 5'),
                    ({'project__exact': 'Project name 0'}, lambda node: node.config.core.project().project.name == 'Project name 0'),
                    ({'type__exact': 'wireless'}, lambda node: node.config.core.type().type == 'wireless'),
                    ({'name__exact': 'Node 5'}, lambda node: node.config.core.general().name == 'Node 5'),
                    ({'project__iexact': 'Project NAME 0'}, lambda node: node.config.core.project().project.name == 'Project name 0'),
                    ({'type__iexact': 'wireLess'}, lambda node: node.config.core.type().type == 'wireless'),
                    ({'name__iexact': 'nODe 5'}, lambda node: node.config.core.general().name == 'Node 5'),
                    ({'project__icontains': 'ProjecT'}, lambda node: True), # All nodes are in projects.
                    ({'type__in': 'wireless,server'}, lambda node: node.config.core.type().type in ('wireless', 'server')),
                    ({'type__in': ['wireless', 'server']}, lambda node: node.config.core.type().type in ('wireless', 'server')),
                    ({'status__monitored__in': 'true,false'}, lambda node: node.monitoring.core.status().monitored in (True, False)),
                    ({'status__monitored__in': ['true', 'false']}, lambda node: node.monitoring.core.status().monitored in (True, False)),
                    ({'status__health__in': ','.join(health_filter)}, lambda node: node.monitoring.core.status().health in health_filter),
                    ({'status__health__in': health_filter}, lambda node: node.monitoring.core.status().health in health_filter),
                    ({'status__monitored__isnull': 'true'}, lambda node: node.monitoring.core.status().monitored is None),
                    ({'last_seen__year': '2014'}, lambda node: True), # All nodes are in 2014.
                    ({'last_seen__year': '2013'}, lambda node: False), # No nodes are in 2014.
                    ({'last_seen__gt': '2014-11-05 01:05:10+0000'}, lambda node: node.monitoring.core.general().last_seen > self.initial_time + datetime.timedelta(seconds=10)),
                    ({'last_seen__range': '2014-11-05 01:05:10+0000,2014-11-05 01:05:20+0000'}, lambda node: self.initial_time + datetime.timedelta(seconds=10) <= node.monitoring.core.general().last_seen <= self.initial_time + datetime.timedelta(seconds=20)),
                    ({'last_seen__range': ['2014-11-05 01:05:10+0000', '2014-11-05 01:05:20+0000']}, lambda node: self.initial_time + datetime.timedelta(seconds=10) <= node.monitoring.core.general().last_seen <= self.initial_time + datetime.timedelta(seconds=20)),
                    # Nodes in the space interval match nodes in the time interval, so we can use that to filter the test list.
                    ({'location__geolocation__bboverlaps': json.dumps({'type': 'Polygon', 'coordinates': [[[10, 40], [10.1, 40], [10.1, 40.1], [10, 40.1], [10, 40]]]})}, lambda node: node.monitoring.core.general().last_seen <= self.initial_time + datetime.timedelta(seconds=10)),
                    ({'location__geolocation__bboverlaps': str({'type': 'Polygon', 'coordinates': [[[10, 40], [10.1, 40], [10.1, 40.1], [10, 40.1], [10, 40]]]})}, lambda node: node.monitoring.core.general().last_seen <= self.initial_time + datetime.timedelta(seconds=10)),
                    ({'location__geolocation__bboverlaps': {'type': 'Polygon', 'coordinates': [[[10, 40], [10.1, 40], [10.1, 40.1], [10, 40.1], [10, 40]]]}}, lambda node: node.monitoring.core.general().last_seen <= self.initial_time + datetime.timedelta(seconds=10)),
                ):
                    kwargs = {
                        'offset': offset,
                        'limit': limit,
                    }
                    kwargs.update(field_filter)
                    data = self.get_list('node', **kwargs)

                    filtered_nodes = [node.uuid for node in filter(filter_function, self.nodes)]
                    nodes = data['objects']
                    self.assertEqual(filtered_nodes[offset:offset + limit if limit else None], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, filter=%s' % (offset, limit, field_filter))

                    key = field_filter.keys()[0]
                    value = field_filter.values()[0]
                    if not isinstance(value, list):
                        value = [value]
                    value = [v if isinstance(v, basestring) else str(v) for v in value]
                    uri_filter = '&'.join(['%s=%s' % (key, urllib.quote(v)) for v in value])

                    limit = limit or resources.NodeResource._meta.max_limit

                    if 0 < offset < limit:
                        previous_limit = offset
                    else:
                        previous_limit = limit

                    self.assertMetaEqual({
                        u'total_count': len(filtered_nodes),
                        u'limit': limit,
                        u'offset': offset,
                        u'nonfiltered_count': 45,
                        u'next': u'%s?%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), uri_filter, limit, offset + limit) if limit and len(filtered_nodes) > offset + limit else None,
                        u'previous': u'%s?%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), uri_filter, previous_limit, offset - previous_limit) if offset != 0 else None,
                    }, data['meta'])

    @unittest.skip("Does not work, see https://code.djangoproject.com/ticket/22352")
    def test_distance(self):
        for distance in (
            json.dumps(json.dumps({'type': 'Point', 'coordinates': [10.1, 40.1]})),
            str(json.dumps({'type': 'Point', 'coordinates': [10.1, 40.1]})),
            json.dumps({'type': 'Point', 'coordinates': [10.1, 40.1]}),
        ):
            data = self.get_list(
                'node',
                offset=0,
                limit=0,
                distance=distance,
            )

        # TODO: Distance field for each node should be available through API only when it exists (when is enabled through query parameter)
        # TODO: Test sorting by distance
        # TODO: Test filtering by distance

    def test_maintainer(self):
        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                for user in self.users:
                    for global_filter, filter_function in (
                        ('', lambda node: True),
                        ('wireless', lambda node: node.config.core.type().type == 'wireless'),
                        ('node 5', lambda node: node.config.core.general().name == 'Node 5'),
                    ):
                        maintainer = user.username
                        data = self.get_list(
                            'node',
                            offset=offset,
                            limit=limit,
                            maintainer=maintainer,
                            filter=global_filter,
                        )

                        # Nodes for which the user has any permission defined for.
                        all_nodes = [node for node in self.nodes if shortcuts.get_perms(user, node)]
                        filtered_nodes = [node.uuid for node in filter(filter_function, all_nodes)]
                        nodes = data['objects']
                        self.assertEqual(filtered_nodes[offset:offset + limit if limit else None], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, maintainer=%s' % (offset, limit, maintainer))

                        limit = limit or resources.NodeResource._meta.max_limit

                        if 0 < offset < limit:
                            previous_limit = offset
                        else:
                            previous_limit = limit

                        self.assertMetaEqual({
                            u'total_count': len(filtered_nodes),
                            u'limit': limit,
                            u'offset': offset,
                            # A special case, we want maintainer filter to filter also nonfiltered_count.
                            u'nonfiltered_count': len(all_nodes),
                            u'next': u'%s?%smaintainer=%s&format=json&limit=%s&offset=%s' % (
                                self.resource_list_uri('node'),
                                'filter=%s&' % urllib.quote(global_filter) if global_filter else '',
                                urllib.quote(maintainer), limit, offset + limit,
                            ) if limit and len(filtered_nodes) > offset + limit else None,
                            u'previous': u'%s?%smaintainer=%s&format=json&limit=%s&offset=%s' % (
                                self.resource_list_uri('node'),
                                'filter=%s&' % urllib.quote(global_filter) if global_filter else '',
                                urllib.quote(maintainer), previous_limit, offset - previous_limit
                            ) if offset != 0 else None,
                        }, data['meta'])

    def test_schema(self):
        with file(os.path.join(apps.get_app_config('frontend_list').path, 'tests', 'schema.json'), 'r') as f:
            schema = json.load(f)

        data = self.get_schema('node')

        self.assertEqual(schema, data)

    def test_get_detail(self):
        for i, node in enumerate(self.nodes[0:5]):
            data = self.get_detail('node', node.uuid)

            self.assertNodeEqual(i, node, data)

    def test_fields_selection(self):
        for fields, selection in (
            ('', lambda node: self.project(node, {})),
            ('__', lambda node: node),
            ('__uuid', lambda node: self.project(node, {'uuid': 1})),
            ('uuid', lambda node: self.project(node, {'uuid': 1})),
            (['uuid', 'name'], lambda node: self.project(node, {'uuid': 1, 'name': 1})),
            (['uuid', 'status'], lambda node: dict(self.project(node, {'uuid': 1}), status={})),
            (['uuid', 'status__'], lambda node: self.project(node, {'uuid': 1, 'status': 1})),
            (['uuid', 'status__health', 'status__monitored'], lambda node: self.project(node, {'uuid': 1, 'status.health': 1, 'status.monitored': 1})),
            (['uuid', '__health', '__monitored'], lambda node: self.project(node, {'uuid': 1})), # Invalid.
            (['uuid', 'health', 'monitored'], lambda node: self.project(node, {'uuid': 1})), # Invalid.
            ('uuid,status', lambda node: dict(self.project(node, {'uuid': 1}), status={})),
            ('uuid,status__', lambda node: self.project(node, {'uuid': 1, 'status': 1})),
            (['uuid', 'status__health,status__monitored'], lambda node: self.project(node, {'uuid': 1, 'status.health': 1, 'status.monitored': 1})),
        ):
            data = self.get_list(
                'node',
                offset=0,
                limit=0,
                fields=fields,
            )

            nodes = data['objects']
            self.assertEqual(len(self.nodes), len(nodes))

            for i, json_node in enumerate(nodes):
                node = self.nodes[i]
                self.assertNodeEqual(i, node, json_node, selection)

            self.assertEqual({
                u'total_count': 45,
                # We specified 0 for limit in the request, so max limit should be used.
                u'limit': resources.NodeResource._meta.max_limit,
                u'offset': 0,
                u'nonfiltered_count': 45,
                u'next': None,
                u'previous': None,
            }, data['meta'])

    def test_ordering_with_fields_selection(self):
        # Testing if we can still order by a field which is not selected in the output.

        for offset in (0, 4, 7):
            for limit in (0, 5, 20):
                for reverse in (False, True):
                    ordering = '-name' if reverse else 'name'
                    data = self.get_list(
                        'node',
                        offset=offset,
                        limit=limit,
                        order_by=ordering,
                        fields='uuid',
                    )

                    key = lambda node: node.config.core.general().name

                    nodes = data['objects']
                    self.assertEqual([node.uuid for node in sorted(self.nodes, key=key, reverse=reverse)[offset:offset + limit if limit else None]], [node['uuid'] for node in nodes], 'offset=%s, limit=%s, ordering=%s' % (offset, limit, ordering))

                    limit = limit or resources.NodeResource._meta.max_limit

                    if 0 < offset < limit:
                        previous_limit = offset
                    else:
                        previous_limit = limit

                    self.assertMetaEqual({
                        u'total_count': 45,
                        u'limit': limit,
                        u'offset': offset,
                        u'nonfiltered_count': 45,
                        u'next': u'%s?fields=uuid&order_by=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(ordering), limit, offset + limit) if limit and len(self.nodes) > offset + limit else None,
                        u'previous': u'%s?fields=uuid&order_by=%s&format=json&limit=%s&offset=%s' % (self.resource_list_uri('node'), urllib.quote(ordering), previous_limit, offset - previous_limit) if offset != 0 else None,
                    }, data['meta'])
