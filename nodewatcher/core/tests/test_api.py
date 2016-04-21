import datetime
import itertools
import operator
import uuid

from django.contrib.auth import models as auth_models
from django.core import urlresolvers
from django.utils import timezone

from guardian import shortcuts

from nodewatcher.core import models as core_models
from nodewatcher.core.registry.api import test
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.monitor import models as monitor_models


class CoreAPITest(test.RegistryAPITestCase):
    """
    Tests API functionality of all core models. The test assumes that all core
    applications are included.
    """

    def setUp(self):
        self.initial_time = datetime.datetime(2014, 11, 5, 1, 5, 0, tzinfo=timezone.utc)

        super(CoreAPITest, self).setUp()

    def setUpNode(self, index, node):
        # General node information.
        node.config.core.general(
            create=cgm_models.CgmGeneralConfig,
            name='Node %s' % index,
        )

        # Password.
        node.config.core.authentication(
            create=cgm_models.PasswordAuthenticationConfig,
            password='my password %s' % index
        ).save()

        # Router IDs.
        for j in [1, 2, 3]:
            node.config.core.routerid(
                create=core_models.StaticIpRouterIdConfig,
                address='127.0.%d.%d' % (index, j),
            ).save()

        # Last seen / first seen.
        node.monitoring.core.general(
            create=monitor_models.GeneralMonitor,
            first_seen=self.initial_time,
            last_seen=self.initial_time + datetime.timedelta(seconds=index),
        )

    def test_api_urls(self):
        self.assertEquals(urlresolvers.reverse('apiv2:node-list'), '/api/v2/node/')

    def test_cors_headers(self):
        response = self.client.options(urlresolvers.reverse('apiv2:node-list'), HTTP_ORIGIN='127.0.0.1')
        self.assertEquals(response['Access-Control-Allow-Origin'], '*')
        self.assertItemsEqual(response['Access-Control-Allow-Methods'].split(', '), ['GET', 'HEAD', 'OPTIONS'])
        self.assertEquals(response['Access-Control-Max-Age'], '86400')

    def test_read_only(self):
        response = self.client.post(urlresolvers.reverse('apiv2:node-list'))
        self.assertEquals(response.status_code, 405)
        response = self.client.put(urlresolvers.reverse('apiv2:node-list'))
        self.assertEquals(response.status_code, 405)
        response = self.client.patch(urlresolvers.reverse('apiv2:node-list'))
        self.assertEquals(response.status_code, 405)
        response = self.client.delete(urlresolvers.reverse('apiv2:node-list'))
        self.assertEquals(response.status_code, 405)

    def test_limit(self):
        response = self.get_node_list({'offset': 0, 'limit': 0})
        self.assertEquals(len(response.data['results']), len(self.nodes))
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        response = self.get_node_list({'offset': 0, 'limit': 10})
        self.assertEquals(len(response.data['results']), 10)
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertEquals(response.data['next'], 'http://testserver/api/v2/node/?limit=10&offset=10')
        self.assertEquals(response.data['previous'], None)

        response = self.get_node_list({'offset': 10, 'limit': 10})
        self.assertEquals(len(response.data['results']), 10)
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertEquals(response.data['next'], 'http://testserver/api/v2/node/?limit=10&offset=20')
        self.assertEquals(response.data['previous'], 'http://testserver/api/v2/node/?limit=10')

    def test_projection(self):
        # Request without any projections should just return node uuids.
        self.assertResponseWithoutProjections(self.get_node_list({'limit': 0}))

        # Project config:core.general__name.
        response = self.get_node_list({'fields': 'config:core.general__name'})
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.general'])
            self.assertDataKeysEqual(item['config']['core.general'], ['name'])

            node = self.nodes[item['@id']]
            self.assertEquals(item['config']['core.general']['name'], node.config.core.general().name)

        # Project config:core.general.
        response = self.get_node_list({'fields': 'config:core.general'})
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.general'])
            self.assertDataKeysEqual(item['config']['core.general'], ['name', 'platform', 'router', 'build_channel', 'version'])

            node = self.nodes[item['@id']]
            self.assertEquals(item['config']['core.general']['name'], node.config.core.general().name)

        # Project an invalid registry point.
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'invalidregistrypoint:core.general__name'}))
        # Project an invalid registry id.
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'config:invalid.registry.id__name'}))
        # Project an invalid field.
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'config:core.general__invalidfield'}))
        # Project some invalid expressions.
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'core.general__name'}))
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'config:core.general__'}))
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'config:core.general[]'}))
        self.assertResponseWithoutProjections(self.get_node_list({'fields': 'config:core.general[foo]'}))

        # Project config:core.routerid.
        response = self.get_node_list({'fields': 'config:core.routerid'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.routerid'])

            node = self.nodes[item['@id']]
            self.assertIsInstance(item['config']['core.routerid'], list)
            self.assertEquals(len(item['config']['core.routerid']), 3)
            for router_id in item['config']['core.routerid']:
                self.assertDataKeysEqual(item['config']['core.routerid'][0], ['router_id', 'rid_family', 'address'])

            self.assertItemsEqual(
                [rid['router_id'] for rid in item['config']['core.routerid']],
                [rid.router_id for rid in node.config.core.routerid()]
            )

        # Project config:core.routerid[router_id="127.0.0.1"].
        response = self.get_node_list({'fields': 'config:core.routerid[router_id="127.0.0.1"]'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.routerid'])

            node = self.nodes[item['@id']]
            self.assertIsInstance(item['config']['core.routerid'], list)
            if node.config.core.general().name == 'Node 0':
                # Only the first node should have matching router IDs.
                self.assertEquals(len(item['config']['core.routerid']), 1)
                self.assertDataKeysEqual(item['config']['core.routerid'][0], ['router_id', 'rid_family', 'address'])
            else:
                # All other nodes should still have a core.routerid section, but it should be an empty array.
                self.assertItemsEqual(item['config']['core.routerid'], [])

        # Project config:core.routerid[router_id="127.0.0.1"]__router_id.
        response = self.get_node_list({'fields': 'config:core.routerid[router_id="127.0.0.1"]__router_id'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.routerid'])

            node = self.nodes[item['@id']]
            self.assertIsInstance(item['config']['core.routerid'], list)
            if node.config.core.general().name == 'Node 0':
                # Only the first node should have matching router IDs.
                self.assertEquals(len(item['config']['core.routerid']), 1)
                self.assertDataKeysEqual(item['config']['core.routerid'][0], ['router_id'])
            else:
                # All other nodes should still have a core.routerid section, but it should be an empty array.
                self.assertItemsEqual(item['config']['core.routerid'], [])

        # Project multiple fields.
        response = self.get_node_list({'fields': ['config:core.general', 'config:core.routerid', 'monitoring:core.general']})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config', 'monitoring'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.general', 'core.routerid'])
            self.assertItemsEqual(item['monitoring'].keys(), ['core.general'])

            node = self.nodes[item['@id']]
            self.assertEquals(item['config']['core.general']['name'], node.config.core.general().name)
            self.assertIsInstance(item['config']['core.routerid'], list)
            self.assertEquals(len(item['config']['core.routerid']), 3)
            for router_id in item['config']['core.routerid']:
                self.assertDataKeysEqual(item['config']['core.routerid'][0], ['router_id', 'rid_family', 'address'])

            self.assertDataKeysEqual(item['monitoring']['core.general'], ['first_seen', 'last_seen', 'uuid', 'firmware'])

    def test_filter(self):
        # Filter equality.
        response = self.get_node_list({'filters': 'config:core.general__name="Node 0"'})
        self.assertEquals(response.data['count'], 1)
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'fields': 'config:core.general', 'filters': 'config:core.general__name="Node 0"'})
        self.assertEquals(response.data['count'], 1)
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.general'])
            self.assertDataKeysEqual(item['config']['core.general'], ['name', 'platform', 'router', 'build_channel', 'version'])

            node = self.nodes[item['@id']]
            self.assertEquals(node.config.core.general().name, 'Node 0')
            self.assertEquals(item['config']['core.general']['name'], 'Node 0')

        # Filter with __contains.
        response = self.get_node_list({'filters': 'config:core.general__name__contains="Node"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.general__name__contains="node"'})
        self.assertEquals(response.data['count'], 0)
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.general__name__icontains="node"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        # Filter multiple fields at once.
        response = self.get_node_list({'filters': 'config:core.general__name__contains="Node",config:core.routerid__router_id__contains="127"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.general__name__contains="Node",config:core.routerid__router_id__contains="555"'})
        self.assertEquals(response.data['count'], 0)
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({
            'filters': 'config:core.general__name__contains="Node",config:core.routerid__router_id__contains="127"',
            'fields': 'config:core.routerid__router_id'
        })
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.routerid'])

            node = self.nodes[item['@id']]
            self.assertIsInstance(item['config']['core.routerid'], list)
            self.assertEquals(len(item['config']['core.routerid']), 3)
            for router_id in item['config']['core.routerid']:
                self.assertDataKeysEqual(item['config']['core.routerid'][0], ['router_id'])

            self.assertItemsEqual(
                [rid['router_id'] for rid in item['config']['core.routerid']],
                [rid.router_id for rid in node.config.core.routerid()]
            )

        # Filter with complex expressions.
        response = self.get_node_list({
            'filters': 'config:core.general__name__contains="Node",(config:core.general__name="Node 0"|config:core.general__name="Node 1")',
            'fields': 'config:core.general__name'
        })
        self.assertEquals(response.data['count'], 2)
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['config'])
            self.assertIn(item['@id'], self.nodes)
            self.assertItemsEqual(item['config'].keys(), ['core.general'])
            self.assertIn(item['config']['core.general']['name'], ['Node 0', 'Node 1'])

        # Filter by invalid fields.
        response = self.get_node_list({'filters': 'invalidregpoint:core.general__name__contains="Node 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:strange.registry.id__name__contains="Node 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.general__invalidfield="Node 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.general__invalidfield__contains="Node 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

    def test_ordering(self):
        test_cases = [
            ('config', 'core.general', 'name'),
            ('monitoring', 'core.general', 'last_seen'),
        ]

        for num_fields in xrange(1, len(test_cases) + 1):
            for fields in zip(itertools.permutations(test_cases, num_fields), itertools.product(*itertools.repeat([True, False], num_fields))):
                ordering = ','.join(['%s%s:%s__%s' % (('-' if field[1] else '',) + field[0]) for field in zip(*fields)])
                nodes_by_order_key = self.nodes.values()
                for field, reverse in zip(*fields)[::-1]:
                    get_registry_item = operator.attrgetter('%s.%s' % (field[0], field[1]))
                    get_field = operator.attrgetter('.'.join(field[2].split('__')))
                    nodes_by_order_key.sort(key=lambda node: get_field(get_registry_item(node)()), reverse=reverse)

                response = self.get_node_list({'fields': 'config:core.general', 'ordering': ordering})
                for base_item, item in zip(nodes_by_order_key, response.data['results']):
                    self.assertDataKeysEqual(item, ['config'])
                    self.assertEquals(item['@id'], str(base_item.uuid))
                    self.assertItemsEqual(item['config'].keys(), ['core.general'])

    def test_sensitive_data(self):
        def check_authentication_results(response, has_subfield=True):
            for item in response.data['results']:
                self.assertDataKeysEqual(item, ['config'])
                self.assertIn(item['@id'], self.nodes)

                if has_subfield:
                    self.assertItemsEqual(item['config'].keys(), ['core.authentication'])
                    self.assertIsInstance(item['config']['core.authentication'], list)
                    self.assertEquals(len(item['config']['core.authentication']), 1)

                    for authentication in item['config']['core.authentication']:
                        self.assertDataKeysEqual(authentication, [])
                else:
                    self.assertItemsEqual(item['config'].keys(), [])

        # Check projection of sensitive fields (without field projection).
        response = self.get_node_list({'fields': 'config:core.authentication'})
        check_authentication_results(response)

        # Check projection of sensitive fields (with field projection).
        response = self.get_node_list({'fields': 'config:core.authentication__password'})
        check_authentication_results(response, False)

        # Check filter by sensitive fields.
        response = self.get_node_list({'filters': 'config:core.authentication__password="my password 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        response = self.get_node_list({'filters': 'config:core.authentication__password__contains="my password 0"'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)

        # Check ordering by sensitive fields. The result should only be sorted by name in
        # reverse as the password sort should be ignored.
        response = self.get_node_list({'ordering': 'config:core.authentication__password,-config:core.general__name'})
        self.assertEquals(response.data['count'], len(self.nodes))
        self.assertResponseWithoutProjections(response)
        for base_item, item in zip(sorted(self.nodes.values(), key=lambda node: node.config.core.general().name, reverse=True), response.data['results']):
            self.assertDataKeysEqual(item, [])
            self.assertEquals(item['@id'], str(base_item.uuid))

    def test_json_ld(self):
        pass
