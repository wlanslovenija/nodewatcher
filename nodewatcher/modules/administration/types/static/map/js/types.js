(function ($) {
    //
    // Register map extenders
    //

    // Create a marker for each location
    $.nodewatcher.map.extendNode(function(node) {
        if (node.data.t && !_.isUndefined(node.marker)) {
            console.log(node);
            var marker = node.marker;
            // Replace icon with div icon if required
            marker.icon = (marker.icon && marker.icon.className) ? marker.icon : L.divIcon();

            var icon = "missing";

            if ($.nodewatcher.nodeType && $.nodewatcher.nodeType[node.data.t]) {
                var ntype = $.nodewatcher.nodeType[node.data.t];
                icon = ntype['icon'];
            }

            marker.html = $.nodewatcher.theme.iconHtml(icon);
            marker.icon.className = marker.icon.className + " map-node-" + icon;
            return marker;
            
        } else {
            return node.marker;
        }
    });

})(jQuery);
