(function ($) {
    $(window).on('map:init', function (e) {
        var detail = e.originalEvent ? e.originalEvent.detail : e.detail;
        var map = detail.map;

        // TODO: Some kind of loading indicator

        $.ajax({
            'url': "/api/v1/stream/?format=json&tags__module=topology&limit=1",
        }).done(function(data) {
            var streamId = data.objects[0].id;
            var latestTimestamp = moment(data.objects[0].latest_datapoint).unix();
            $.ajax({
                'url': "/api/v1/stream/" + streamId + "/?format=json&reverse=true&limit=1&start_exclusive=" + latestTimestamp,
            }).done(function(data) {
                var graph = data.datapoints[0].v;
                var nodes = [];
                var edges = [];
                var nodeIndex = {};

                $.each(graph.v, function(index, vertex) {
                    nodes.push({
                        'index': index,
                        'data': vertex,
                    });
                    nodeIndex[vertex.i] = index;
                });

                $.each(graph.e, function(index, edge) {
                    edges.push({
                        'source': nodeIndex[edge.f],
                        'target': nodeIndex[edge.t],
                        'data': edge,
                    });
                });

                $.nodewatcher.map.extend(map, nodes, edges);
            });
        });
    });
})(jQuery);
