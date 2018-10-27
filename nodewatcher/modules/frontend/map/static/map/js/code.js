(function ($) {
    $(window).on('map:init', function (e) {
        var detail = e.originalEvent ? e.originalEvent.detail : e.detail;
        var map = detail.map;
        
        //Fulscreen map button
        map.addControl(new L.Control.Fullscreen());
        
        //Adding the sidebar to the map
        //Adds the HTML div with id="sidebar" from map.html to the map
        var sidebar = L.control.sidebar({ container: 'sidebar', closeButton: false, position: 'right'}).addTo(map);
        
        // TODO: Some kind of loading indicator
        
        //Time selection for the recently offline nodes
        //Currently it is 24h since now-1h
        var time_start = new Date();
        var time_stop = new Date();
        time_start.setHours(time_start.getHours() - 25);
        time_stop.setHours(time_stop.getHours() - 1);
        
        //APIv2 request for the recently offline nodes
        $.ajax({
            'url': '/api/v2/node/?format=json&limit=1&&filters=monitoring:core.general__last_seen__gt="' + time_start.toISOString() + '",monitoring:core.general__last_seen__lt="' + time_stop.toISOString() + '"',
        }).done(function(data) {
            for(var i = 1; i < data.count; i++) {
                $.ajax({
                    'url': '/api/v2/node/?format=json&limit=1&fields=monitoring:core.general__last_seen&fields=config:core.location&fields=config:core.general&fields=config:core.type&filters=monitoring:core.general__last_seen__gt="' + time_start.toISOString() + '",monitoring:core.general__last_seen__lt="' + time_stop.toISOString() + '"&offset=' + (i - 1),
                }).done(function(data) {
                    var node = {
                        'data': {
                            'n': data.results[0]["config"]["core.general"]["name"],                         //node name
                            'i': data.results[0]["@id"],                                                    //node id
                            't': data.results[0]["config"]["core.type"]["type"],                            //node type
                            'l': (data.results[0]["config"]["core.location"]["geolocation"] ? data.results[0]["config"]["core.location"]["geolocation"]["coordinates"] : null),  //node coordinates
                            'api': "v2",                                                                    //api version which was used to get the data
                        },
                    }
                    sidebarTableAddNode(node,"recently-offline-table");
                });
            }
        });
        
        //APIv1 request for all the currently active nodes with the location parameter set
        $.ajax({
            'url': "/api/v1/stream/?format=json&tags__module=topology&limit=1",
        }).done(function(data) {
            var streamId = data.objects[0].id;
            var latestTimestamp = moment(data.objects[0].latest_datapoint).unix();
            $.ajax({
                'url': "/api/v1/stream/" + streamId + "/?format=json&reverse=true&limit=1&start=" + latestTimestamp,
            }).done(function(data) {
                var graph = data.datapoints[0].v;
                var nodes = [];
                var edges = [];
                var nodeIndex = {};
                
                //storing each node data
                $.each(graph.v, function(index, vertex) {
                    nodes.push({
                        'index': index,     //index of the node
                        'data': vertex,     //data which stores the name, id, type and coordinates
                    });
                    nodeIndex[vertex.i] = index;
                });
                
                //storing the links between the nodes
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
