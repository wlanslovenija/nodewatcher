(function ($) {
    //
    // Register map extenders
    //

    // Create a marker for each location
    $.nodewatcher.map.extendNode(function(node) {
        if (node.data.t && !_.isUndefined(node.marker)) {
            var marker = node.marker;
            // Replace icon with div icon if required
            var icon = (marker._icon && marker._icon.options.className) ? marker._icon : L.divIcon();
            //var icon = L.divIcon();

            var type = "missing";

            if ($.nodewatcher.nodeType && $.nodewatcher.nodeType[node.data.t]) {
                var ntype = $.nodewatcher.nodeType[node.data.t];
                type = ntype['icon'];
            }

            icon.options.html = $.nodewatcher.theme.iconHtml(type);
            icon.options.className = "map-node " + type;
            icon.options.iconSize = null;
            
            marker.setIcon(icon);
            return marker;
            
        } else {
            return node.marker;
        }
    });

})(jQuery);
