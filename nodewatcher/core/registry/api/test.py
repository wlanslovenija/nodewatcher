import json
import uuid

from django.contrib.auth import models as auth_models
from django.core import urlresolvers

from guardian import shortcuts
from rest_framework import test

from nodewatcher.core import models as core_models


class RegistryAPITestCase(test.APITestCase):
    def setUp(self):
        super(RegistryAPITestCase, self).setUp()

        # Create some users.
        self.users = []
        for i in range(3):
            user = auth_models.User.objects.create_user(
                username='username%s' % i,
            )
            user.save()
            self.users.append(user)

        # Create some nodes.
        self.nodes = {}
        for i in range(45):
            # We generate UUIDs so that they are nicely in sequence so that
            # default REST API ordering does not really change the order.
            node = core_models.Node(uuid=str(uuid.UUID(int=i, version=1)))
            node.save()

            # Assign maintainer permissions.
            maintainer = self.users[i % len(self.users)]
            shortcuts.assign_perm('change_node', maintainer, node)
            shortcuts.assign_perm('delete_node', maintainer, node)
            shortcuts.assign_perm('reset_node', maintainer, node)
            shortcuts.assign_perm('generate_firmware', maintainer, node)

            # Invoke custom node setup.
            self.setUpNode(i, node)

            self.nodes[str(node.uuid)] = node

    def setUpNode(self, index, node):
        pass

    def assertDataKeysEqual(self, a, b):
        keys = [key for key in a.keys() if key[0] != '@']
        self.assertItemsEqual(keys, b)

    def assertRegistryItemHasProjection(self, item, registration_point, registry_id):
        self.assertDataKeysEqual(item, ['uuid', registration_point])
        self.assertIn(item['uuid'], self.nodes)
        self.assertItemsEqual(item['config'].keys(), [registry_id])

    def assertResponseWithoutProjections(self, response):
        for item in response.data['results']:
            self.assertDataKeysEqual(item, ['uuid'])
            self.assertIn(item['uuid'], self.nodes)

    def get_node_list(self, *args, **kwargs):
        response = self.client.get(urlresolvers.reverse('apiv2:node-list'), *args, **kwargs)
        # Manually deserialize content instead of using response.data as the latter is sometimes not raw JSON.
        response.data = json.loads(response.content)
        return response
