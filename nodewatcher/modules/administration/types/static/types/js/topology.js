(function ($) {
    //
    // Register topology extenders
    //

    // Node color based on node type
    $.nodewatcher.topology.extendNode(function(node) {
        node.style("fill", function(d) {
            switch (d.data.t) {
                case "server": return "#645192";
                case "wireless": return "#4A9372";
                case "test": return "#D4C56C";
                default: return "#D4886C";
            }
        });
    });
})(jQuery);
