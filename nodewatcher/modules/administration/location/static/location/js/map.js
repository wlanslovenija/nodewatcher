(function ($) {
    //
    // Register map extenders
    //

    // Create a marker for each location
    $.nodewatcher.map.extendNode(function(node) {
        if (node.data.l) {
            sidebarTableAddNode(node,"node-list-table");  //Add the node to the sidebar active node list
            return L.marker({lng: node.data.l[0], lat: node.data.l[1]}).bindPopup('Name: <a href="../node/' + node.data.i + '">' + node.data.n + '</a><br>Type: ' + node.data.t);  //Show a popup when a node is selected with its name and type
        }
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
