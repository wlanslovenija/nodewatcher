from nodewatcher.core.registry.api import test

from . import models


class ProjectAPITest(test.RegistryAPITestCase):
    def setUp(self):
        # Create some projects.
        self.projects = []
        for i in xrange(3):
            project = models.Project(
                name='Project %d' % i,
                description='This is a nice project number %d.' % i,
                is_default=(i == 0),
                location='POINT(13.579058 45.967976)'
            )
            project.save()

            self.projects.append(project)

        super(ProjectAPITest, self).setUp()

    def setUpNode(self, index, node):
        node.config.core.project(
            create=models.ProjectConfig,
            project=self.projects[index % len(self.projects)]
        )

    def test_projection(self):
        # Config item projection.
        response = self.get_node_list({'fields': 'config:core.project'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertRegistryItemHasProjection(item, 'config', 'core.project')
            self.assertDataKeysEqual(item['config']['core.project'], ['project'])

            node = self.nodes[item['@id']]
            self.assertEquals(item['config']['core.project']['project'], node.config.core.project().project.pk)

        # Project instance projection.
        response = self.get_node_list({'fields': 'config:core.project__project'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertRegistryItemHasProjection(item, 'config', 'core.project')
            self.assertDataKeysEqual(item['config']['core.project'], ['project'])

            node = self.nodes[item['@id']]
            project = node.config.core.project().project
            item_project = item['config']['core.project']['project']
            self.assertEquals(item_project['name'], project.name)
            self.assertEquals(item_project['description'], project.description)
            self.assertEquals(item_project['is_default'], project.is_default)
            self.assertIsInstance(item_project['location'], dict)
            self.assertEquals(item_project['location']['type'], 'Point')
            self.assertEquals(item_project['location']['coordinates'], [13.579058, 45.967976])

        # Project name projection.
        response = self.get_node_list({'fields': 'config:core.project__project__name'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertRegistryItemHasProjection(item, 'config', 'core.project')
            self.assertDataKeysEqual(item['config']['core.project'], ['project'])
            self.assertDataKeysEqual(item['config']['core.project']['project'], ['name'])

            node = self.nodes[item['@id']]
            self.assertEquals(item['config']['core.project']['project']['name'], node.config.core.project().project.name)
