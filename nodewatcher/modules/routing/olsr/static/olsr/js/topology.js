(function ($) {
    //
    // Register topology extenders
    //

    // Link color based on link quality
    $.nodewatcher.topology.extendLink(function(link) {
        link.filter(function(d, i) {
            try {
                return d.data.proto == "olsr";
            } catch (e) {
                return false;
            }
        }).style("stroke", function(d) {
            var etx = d.data.metrics.etx;
            if (etx >= 1.0 && etx <= 2.0)
                return "#00FF00";
            else if (etx > 2.0 && etx <= 5.0)
                return "#0000FF";
            else
                return "#FF0000";
        });
    });
})(jQuery);
