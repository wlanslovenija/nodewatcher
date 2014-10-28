(function ($) {
    //
    // Register map extenders
    //

    // Color polylines based on link quality
    $.nodewatcher.map.extendLink(function(source, target, link) {
        if (link.line && link.data.proto == "olsr") {
            var etx = link.data.etx;
            if (etx >= 1.0 && etx <= 2.0)
                link.line.setStyle({color: "#00FF00"});
            else if (etx > 2.0 && etx <= 5.0)
                link.line.setStyle({color: "#0000FF"});
            else
                link.line.setStyle({color: "#FF0000"});
        }

        return link.line;
    });
})(jQuery);
