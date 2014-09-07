(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    };

    var nodeExtenders = [];
    var linkExtenders = [];

    $.nodewatcher.topology = {};

    $.nodewatcher.topology.extendNode = function(extender) {
        nodeExtenders.push(extender);
    };

    $.nodewatcher.topology.extendLink = function(extender) {
        linkExtenders.push(extender);
    };

    $.nodewatcher.topology.extend = function(node, link) {
        $.each(nodeExtenders, function(index, extender) {
            extender(node);
        });

        $.each(linkExtenders, function(index, extender) {
            extender(link);
        });
    };

    //
    // Register core extenders
    //

    // Default node fill color
    $.nodewatcher.topology.extendNode(function(node) {
        node.style("fill", function(d) { return "#73B55B"; });
    });

    // Default name as title
    $.nodewatcher.topology.extendNode(function(node) {
        node.append("title").text(function(d) { return d.data.n; });
    });
})(jQuery);
