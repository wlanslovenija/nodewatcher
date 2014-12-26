import datetime
import uuid

from django.core import urlresolvers
from django.contrib.auth import models as auth_models

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

        self.initial_time = datetime.datetime(2014, 11, 5, 1, 5, 0)

        for i in range(45):
            node = core_models.Node(uuid=uuid.uuid4())
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
                last_seen=self.initial_time + datetime.timedelta(seconds=i * 97),
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

    def resource_list_uri(self, resource_name):
        return urlresolvers.reverse('api:api_dispatch_list', kwargs={'api_name': self.api_name, 'resource_name': resource_name})

    def get_list(self, **kwargs):
        response = self.api_client.get(self.node_list, data=kwargs)

        self.assertValidJSONResponse(response)

        return self.deserialize(response)
