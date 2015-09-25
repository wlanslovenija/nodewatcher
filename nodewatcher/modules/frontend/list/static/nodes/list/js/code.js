(function ($) {
    function renderTimeAgo(data, type, row, meta) {
        if (type !== 'display') 
            return data;

        var t = moment(data);
        if (!t.isValid())
            return "<em>never</em>";
        
        // TODO: custom date formats, refresing?
        var output = $('<span/>').attr('title', t.format($.nodewatcher.theme.dateFormat)).addClass('time').append(t.fromNow());

        return output.wrap('<span/>').parent().html();

    }

    function renderRoutingTopology(data, type, row, meta) {
        var output = $('<span/>');

        // Sort by protocol name to get a consistent order everywhere.
        data = _.sortBy(data, 'protocol');

        _.each(data, function (info, index) {
            // TODO: Structure this better. Use <dl>, <dt> and <dd>.
            var obj = $('<span />');
            obj.attr('title', info.protocol);
            obj.append(info.link_count);

            if (index < data.length - 1)
                obj.append('&nbsp;·&nbsp;');

            output.append(obj);
        });

        return output.html();
    }

    $(document).ready(function () {
        $('.node-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    {'data': 'type', 'width': 0, 'render': $.nodewatcher.renderNodeType(table)},
                    {'data': 'name', 'render': $.tastypie.nodeNameRender(table)},
                    {'data': 'router_id[].router_id', 'orderByField': 'router_id__router_id'},
                    {'data': 'last_seen', 'render': renderTimeAgo},
                    {'data': 'status.network', 'render': $.nodewatcher.renderStatus(table, 'Network'), 'class': 'center', 'width': '20px'},
                    {'data': 'status.monitored', 'render': $.nodewatcher.renderStatus(table, 'Monitored'), 'class': 'center', 'width': '20px'},
                    {'data': 'status.health', 'render': $.nodewatcher.renderStatus(table, 'Health'), 'class': 'center', 'width': '20px'},
                    {'data': 'routing_topology.', 'render': renderRoutingTopology, 'orderByField': 'routing_topology__link_count'},
                    {'data': 'project'},
                    // So that user can search by UUID
                    {'data': 'uuid', 'visible': false}
                ],
                // Grouping, we fix sorting by (hidden) type column
                //'orderFixed': [],
                // And make default sorting by name column
                'order': [[0, 'asc'],[1, 'asc']],
                //'drawCallback': $.tastypie.groupDrawCallback(table),
                'language': {
                    // TODO: Make strings translatable
                    'zeroRecords': "No matching nodes found.",
                    'emptyTable ': "There are currently no nodes recorded/connected.",
                    'info': "_START_ to _END_ of _TOTAL_ nodes shown",
                    'infoEmpty': "0 nodes shown",
                    'infoFiltered': "(from _MAX_ all nodes)",
                    'infoPostFix': "",
                    'search': "Filter:"
                }
            });
        });
    });
})(jQuery);
