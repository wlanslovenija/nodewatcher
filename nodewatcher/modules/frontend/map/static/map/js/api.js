(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    };

    var nodeExtenders = [];
    var linkExtenders = [];

    $.nodewatcher.map = {};

    $.nodewatcher.map.extendNode = function(extender) {
        nodeExtenders.push(extender);
    };

    $.nodewatcher.map.extendLink = function(extender) {
        linkExtenders.push(extender);
    };

    $.nodewatcher.map.extend = function(map, nodes, links) {
        $.each(nodeExtenders, function(index, extender) {
            $.each(nodes, function(nodeIndex, node) {
                node.marker = extender(node);
            });
        });

        var cluster = new L.MarkerClusterGroup({spiderfyDistanceMultiplier: 3, maxClusterRadius: 20,
            disableClusteringAtZoom: 13});

        $.each(nodes, function(index, node) {
            if (node.marker)
                cluster.addLayer(node.marker);
        });

        map.addLayer(cluster);

        $.each(linkExtenders, function(index, extender) {
            $.each(links, function(index, link) {
                var source = nodes[link.source];
                var target = nodes[link.target];

                if (source.marker && target.marker)
                    link.line = extender(source, target, link);
            });
        });

        $.each(links, function(index, link) {
            if (link.line)
                link.line.addTo(map);
        });
    };
})(jQuery);
