import uuid

from django.core import urlresolvers

from rest_framework import status

from nodewatcher.core import models as core_models
from nodewatcher.core.generator import models as generator_models
from nodewatcher.core.registry.api import test


class BuildResultAPITest(test.RegistryAPITestCase):
    def setUp(self):
        super(BuildResultAPITest, self).setUp()

        # Create a build version instance.
        self.build_version = generator_models.BuildVersion(
            name='git.1234567'
        )
        self.build_version.save()

        # Create a builder instance.
        self.builder = generator_models.Builder(
            platform='openwrt',
            architecture='ar71xx',
            version=self.build_version,
            host='localhost',
            private_key='key',
        )
        self.builder.save()

        # Create a build channel instance.
        self.build_channel = generator_models.BuildChannel(
            name='stable',
            description='Stable channel.',
            default=True,
        )
        self.build_channel.save()
        self.build_channel.builders.add(self.builder)

        # Create some build results.
        self.build_results = []
        for i in xrange(10):
            build_result = generator_models.BuildResult(
                # We generate UUIDs so that they are nicely in sequence so that
                # default REST API ordering does not really change the order.
                uuid=str(uuid.UUID(int=i, version=1)),
                # Node for user 0 is node 0.
                user=self.users[0],
                node=self.nodes[str(uuid.UUID(int=0, version=1))],
                config={'index': i},
                build_channel=self.build_channel,
                builder=self.builder,
                status=generator_models.BuildResult.PENDING,
            )
            build_result.save()

            self.build_results.append(build_result)

        # Also create some build results for another user.
        self.different_build_results = []
        for i in xrange(10):
            build_result = generator_models.BuildResult(
                # Node for user 1 is node 1.
                user=self.users[1],
                node=self.nodes[str(uuid.UUID(int=1, version=1))],
                config={'index': i},
                build_channel=self.build_channel,
                builder=self.builder,
                status=generator_models.BuildResult.PENDING,
            )
            build_result.save()

            self.different_build_results.append(build_result)

        # Authenticate as user 0 for tests.
        self.client.force_authenticate(self.users[0])

    def setUpNode(self, index, node):
        node.config.core.general(
            create=core_models.GeneralConfig,
            name='Node {}'.format(index),
        )

    def test_api_uris(self):
        # URIs have to be stable.

        self.assertEqual(urlresolvers.reverse('apiv2:buildresult-list'), '/api/v2/build_result/')

    def test_read_only(self):
        build_result_uri = urlresolvers.reverse('apiv2:buildresult-list')

        response = self.client.post(build_result_uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(build_result_uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(build_result_uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(build_result_uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthenticated(self):
        self.client.logout()

        # Unauthenticated users should get no results.
        response = self.client.get(urlresolvers.reverse('apiv2:buildresult-list'), format='json')
        self.assertEqual(len(response.data['results']), 0)

    def test_unauthorized(self):
        # Ensure that we cannot access some other user's results.
        response = self.client.get(
            urlresolvers.reverse('apiv2:buildresult-detail', kwargs={'pk': self.different_build_results[0].uuid}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def assertBuildResultEqual(self, data, build_result):
        self.assertEqual(data['status'], build_result.status)
        self.assertEqual(data['uuid'], str(build_result.uuid))

    def test_detail(self):
        response = self.client.get(
            urlresolvers.reverse('apiv2:buildresult-detail', kwargs={'pk': self.build_results[0].uuid}),
            format='json'
        )
        self.assertBuildResultEqual(response.data, self.build_results[0])

    def test_list(self):
        response = self.client.get(
            urlresolvers.reverse('apiv2:buildresult-list'),
            {'ordering': 'uuid'},
            format='json'
        )
        self.assertEqual(len(response.data['results']), 10)

        for index, item in enumerate(response.data['results']):
            instance = self.build_results[index]
            self.assertBuildResultEqual(item, instance)
