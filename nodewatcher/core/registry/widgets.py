
from leaflet.forms import widgets as leaflet_widgets


class LocationWidget(leaflet_widgets.LeafletWidget):
    """
    A location widget that enables input.
    """

    include_media = True

    def __init__(self, **kwargs):
        """
        Class constructor.
        """

        if 'map_width' in kwargs:
            kwargs['map_width'] = '%spx' % kwargs['map_width']
        if 'map_height' in kwargs:
            kwargs['map_height'] = '%spx' % kwargs['map_height']

        super(LocationWidget, self).__init__(kwargs)
