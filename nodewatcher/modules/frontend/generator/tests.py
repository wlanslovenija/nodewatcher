import datetime
import uuid

from django.contrib.auth import models as auth_models
from django.utils import encoding, timezone, feedgenerator

from django_datastream import test_runner

from nodewatcher.core import models as core_models
from nodewatcher.core.generator import models as generator_models

from . import resources


class BuildResultResourceTest(test_runner.ResourceTestCase):
    namespace = 'api'

    @classmethod
    def setUpClass(cls):
        super(BuildResultResourceTest, cls).setUpClass()

        # Create a node instance and name it.
        cls.node = core_models.Node()
        cls.node.save()

        cls.node.config.core.general(
            create=core_models.GeneralConfig,
            name='Node',
        )

        # Create a user instance.
        cls.user_username = 'username'
        cls.user_password = 'password'
        cls.user = auth_models.User.objects.create_user(
            username=cls.user_username,
            password=cls.user_password,
        )

        # Create a different user instance.
        cls.different_user = auth_models.User.objects.create_user(
            username='different',
            password=cls.user_password,
        )

        # Create a build version instance.
        cls.build_version = generator_models.BuildVersion(
            name='git.1234567'
        )
        cls.build_version.save()

        # Create a builder instance.
        cls.builder = generator_models.Builder(
            platform='openwrt',
            architecture='ar71xx',
            version=cls.build_version,
            host='localhost',
            private_key='key',
        )
        cls.builder.save()

        # Create a build channel instance.
        cls.build_channel = generator_models.BuildChannel(
            name='stable',
            description='Stable channel.',
            default=True,
        )
        cls.build_channel.save()
        cls.build_channel.builders.add(cls.builder)

        # Create some build results.
        cls.build_results = []
        for i in xrange(10):
            build_result = generator_models.BuildResult(
                # We generate UUIDs so that they are nicely in sequence so that
                # default REST API ordering does not really change the order.
                uuid=str(uuid.UUID(int=i, version=1)),
                user=cls.user,
                node=cls.node,
                config={'index': i},
                build_channel=cls.build_channel,
                builder=cls.builder,
                status=generator_models.BuildResult.PENDING,
            )
            build_result.save()

            cls.build_results.append(build_result)

        # Also create some build results for another user.
        cls.different_build_results = []
        for i in xrange(10):
            build_result = generator_models.BuildResult(
                user=cls.different_user,
                node=cls.node,
                config={'index': i},
                build_channel=cls.build_channel,
                builder=cls.builder,
                status=generator_models.BuildResult.PENDING,
            )
            build_result.save()

            cls.different_build_results.append(build_result)

    def setUp(self):
        super(BuildResultResourceTest, self).setUp()

        # Ensure that we are authenticated in tests.
        self.assertTrue(self.api_client.client.login(
            username=self.user_username,
            password=self.user_password,
        ))

    def assertBuildResultEqual(self, i, build_result, json_build_result, selection=lambda result: result):
        self.assertEqual(selection({
            u'uuid': encoding.force_unicode(build_result.uuid),
            u'node': {
                u'uuid': encoding.force_unicode(build_result.node.uuid),
                u'name': build_result.node.config.core.general().name,
                # We manually construct URI to make sure it is like we assume it is.
                u'resource_uri': u'%s%s/' % (self.resource_list_uri('node'), build_result.node.uuid),
            },
            u'build_channel': {
                u'name': build_result.build_channel.name,
                u'description': build_result.build_channel.description,
                u'default': build_result.build_channel.default,
                # We manually construct URI to make sure it is like we assume it is.
                u'resource_uri': u'%s%s/' % (self.resource_list_uri('build_channel'), build_result.build_channel.uuid),
            },
            u'builder': {
                u'platform': build_result.builder.platform,
                u'architecture': build_result.builder.architecture,
                u'version': {
                    u'name': build_result.builder.version.name,
                    # We manually construct URI to make sure it is like we assume it is.
                    u'resource_uri': u'%s%s/' % (self.resource_list_uri('build_version'), build_result.builder.version.uuid),
                },
                # We manually construct URI to make sure it is like we assume it is.
                u'resource_uri': u'%s%s/' % (self.resource_list_uri('builder'), build_result.builder.uuid),
            },
            u'created': feedgenerator.rfc2822_date(build_result.created),
            u'last_modified': feedgenerator.rfc2822_date(build_result.last_modified),
            u'status': build_result.status,
            # We manually construct URI to make sure it is like we assume it is.
            u'resource_uri': u'%s%s/' % (self.resource_list_uri('build_result'), build_result.uuid),
        }), json_build_result)

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

        self.assertEqual('/api/v1/build_result/', self.resource_list_uri('build_result'))
        self.assertEqual('/api/v1/build_result/schema/', self.resource_schema_uri('build_result'))

    def test_read_only(self):
        build_result_uri = '%s%s/' % (self.resource_list_uri('build_result'), self.build_results[0].uuid)

        self.assertHttpMethodNotAllowed(self.api_client.post(self.resource_list_uri('build_result'), format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.put(build_result_uri, format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.patch(build_result_uri, format='json', data={}))
        self.assertHttpMethodNotAllowed(self.api_client.delete(build_result_uri, format='json'))

    def test_unauthenticated(self):
        self.api_client.client.logout()
        self.assertHttpUnauthorized(self.api_client.get(self.resource_list_uri('build_result'), format='json'))

    def test_unauthorized(self):
        # Ensure that we cannot access some other user's results.
        build_result_uri = '%s%s/' % (self.resource_list_uri('build_result'), self.different_build_results[0].uuid)
        self.assertHttpUnauthorized(self.api_client.get(build_result_uri, format='json'))

    def test_get_list_all(self):
        data = self.get_list(
            'build_result',
            offset=0,
            limit=0,
        )

        build_results = data['objects']
        self.assertEqual(len(self.build_results), len(build_results))

        for i, json_build_result in enumerate(build_results):
            build_result = self.build_results[i]
            self.assertBuildResultEqual(i, build_result, json_build_result)

        self.assertEqual({
            u'total_count': len(self.build_results),
            # We specified 0 for limit in the request, so max limit should be used.
            u'limit': resources.BuildResultResource._meta.max_limit,
            u'offset': 0,
            u'nonfiltered_count': len(self.build_results),
            u'next': None,
            u'previous': None,
        }, data['meta'])

    def test_fields_selection(self):
        for fields, selection in (
            ('', lambda result: self.project(result, {})),
            ('__', lambda result: result),
            ('__uuid', lambda result: self.project(result, {'uuid': 1})),
            ('uuid', lambda result: self.project(result, {'uuid': 1})),
            (['uuid', 'status'], lambda result: self.project(result, {'uuid': 1, 'status': 1})),
            (['uuid', 'node__name'], lambda result: self.project(result, {'uuid': 1, 'node.name': 1, 'node.resource_uri': 1})),
        ):
            data = self.get_list(
                'build_result',
                offset=0,
                limit=0,
                fields=fields,
            )

            build_results = data['objects']
            self.assertEqual(len(self.build_results), len(build_results))

            for i, json_build_result in enumerate(build_results):
                build_result = self.build_results[i]
                self.assertBuildResultEqual(i, build_result, json_build_result, selection)

            self.assertEqual({
                u'total_count': len(self.build_results),
                # We specified 0 for limit in the request, so max limit should be used.
                u'limit': resources.NodeResource._meta.max_limit,
                u'offset': 0,
                u'nonfiltered_count': len(self.build_results),
                u'next': None,
                u'previous': None,
            }, data['meta'])
