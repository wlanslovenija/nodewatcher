from nodewatcher.core.registry.api import test

from . import models


class LocationAPITest(test.RegistryAPITestCase):
    def setUp(self):
        self.landmarks = [
            # (Landmark position, node position -- must be within 2km of landmark, polygon containing the nodes).
            ('POINT(14.513288 46.0448141)', 'POINT(14.4982071 46.048937)',
                None),
            ('POINT(15.6527359 46.5537194)', 'POINT(15.6431848 46.547943)',
                'POLYGON((15.5907115 46.5753691, 15.6877521 46.5628489, 15.7021459 46.5163584, 15.5947565 46.5290942, 15.5907115 46.5753691))'),
        ]
        self.landmark_nodes = {}

        super(LocationAPITest, self).setUp()

    def setUpNode(self, index, node):
        landmark, node_position, bbox = self.landmarks[index % len(self.landmarks)]
        node.config.core.location(
            create=models.LocationConfig,
            address="Test street 7",
            country='SI',
            timezone='Europe/Ljubljana',
            defaults={
                'geolocation': node_position,
            }
        )

        self.landmark_nodes.setdefault(landmark, set()).add(node)

    def test_projection(self):
        # Config item projection.
        response = self.get_node_list({'fields': 'config:core.location'})
        self.assertEquals(response.data['count'], len(self.nodes))
        for item in response.data['results']:
            self.assertRegistryItemHasProjection(item, 'config', 'core.location')
            self.assertDataKeysEqual(item['config']['core.location'], ['address', 'country', 'city', 'timezone', 'geolocation', 'altitude'])

            node = self.nodes[item['@id']]
            node_location = node.config.core.location()
            location = item['config']['core.location']
            self.assertEquals(location['address'], node_location.address)
            self.assertEquals(location['country'], node_location.country)
            self.assertEquals(location['timezone'], node_location.timezone.zone)
            self.assertIsInstance(location['geolocation'], dict)

            geolocation = location['geolocation']
            self.assertEquals(geolocation['type'], node_location.geolocation.geom_type)
            self.assertEquals(geolocation['coordinates'], list(node_location.geolocation.coords))

    def test_filter(self):
        for landmark, node_position, bbox in self.landmarks:
            # Distance query (find all nodes within 2km of each landmark).
            response = self.get_node_list({'filters': 'config:core.location__geolocation__dwithin={"%s",distance::2000}' % landmark})
            self.assertEquals(response.data['count'], len(self.landmark_nodes[landmark]))

            # Polygon containment query.
            if bbox is not None:
                response = self.get_node_list({'filters': 'config:core.location__geolocation__bboverlaps="%s"' % bbox})
                self.assertEquals(response.data['count'], len(self.landmark_nodes[landmark]))
