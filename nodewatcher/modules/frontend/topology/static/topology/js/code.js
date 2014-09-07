(function ($) {
    $(document).ready(function () {
        // Create the canvas
        var width = 960;
        var height = 1000;

        var svg = d3.select("#topology").append("svg")
            .attr("width", width)
            .attr("height", height);

        // TODO: Some kind of loading indicator

        $.ajax({
            'url': "/api/v1/stream/?format=json&tags__module=topology&limit=1",
        }).done(function(data) {
            var streamId = data.objects[0].id;
            $.ajax({
                'url': "/api/v1/stream/" + streamId + "/?format=json&reverse=true&limit=1",
            }).done(function(data) {
                var graph = data.datapoints[0].v;
                var nodes = [];
                var edges = [];
                var nodeIndex = {};

                $.each(graph.v, function(index, vertex) {
                    nodes.push({
                        'index': index,
                        'uuid': vertex.i,
                        'name': vertex.n,
                    });
                    nodeIndex[vertex.i] = index;
                });

                $.each(graph.e, function(index, vertex) {
                    edges.push({
                        'source': nodeIndex[vertex.f],
                        'target': nodeIndex[vertex.t],
                        'value': 1,
                    });
                });

                var force = d3.layout.force()
                    .charge(-120)
                    .linkDistance(30)
                    .size([width, height])
                    .nodes(nodes)
                    .links(edges)
                    .start();

                var link = svg.selectAll(".link")
                    .data(edges)
                    .enter().append("line")
                    .attr("class", "link")
                    .style("stroke-width", function(d) { return Math.sqrt(d.value); });

                var node = svg.selectAll(".node")
                    .data(nodes)
                    .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", 5)
                    .style("fill", function(d) { return "#73B55B"; })
                    .call(force.drag);

                node.append("title")
                    .text(function(d) { return d.name; });

                force.on("tick", function() {
                    link.attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });

                    node.attr("cx", function(d) { return d.x; })
                        .attr("cy", function(d) { return d.y; });
                });
            });
        });
    });
})(jQuery);
