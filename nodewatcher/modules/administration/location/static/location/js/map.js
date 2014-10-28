(function ($) {
    //
    // Register map extenders
    //

    // Create a marker for each location
    $.nodewatcher.map.extendNode(function(node) {
        if (node.data.l)
            return L.marker({lng: node.data.l[0], lat: node.data.l[1]});
    });

    // Create a polyline for each link
    $.nodewatcher.map.extendLink(function(source, target, link) {
        return L.polyline([
            source.marker.getLatLng(),
            target.marker.getLatLng(),
        ], {
            'color': '#0000ff',
        });
    });
})(jQuery);
