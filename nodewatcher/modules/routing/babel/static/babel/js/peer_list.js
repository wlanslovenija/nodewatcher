(function ($) {
    function renderTimeAgo(data, type, row, meta) {
        if (type !== 'display')
            return data;

        var t = moment(data);
        if (!t.isValid())
            return "<em>never</em>";

        // TODO: custom date formats, refresing?
        var output = $('<span/>').attr('title', t.format($.nodewatcher.theme.dateFormat)).append(t.fromNow());

        return output.wrap('<span/>').parent().html();

    }

    $(document).ready(function () {
        $('.babel-peer-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    // TODO: How can we generate string from registry, without hardcoding registry relations?
                    {'data': 'peer.name', 'render': $.tastypie.nodeSubdocumentName(table, 'peer'), 'orderByField': 'peer__config_core_generalconfig__name'},
                    {'data': 'last_seen', 'render': renderTimeAgo},
                    {'data': 'reachability'},
                    {'data': 'rxcost'},
                    {'data': 'txcost'},
                    {'data': 'cost'},
                    // We need extra data to render the node column.
                    {'data': 'peer.uuid', 'visible': false}
                ],
                'order': [[0, 'asc']],
                'language': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No Babel peer links found.",
                    'sEmptyTable ': "There are currently no Babel peer links.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ Babel peer links shown",
                    'sInfoEmpty': "0 Babel peer links shown",
                    'sInfoFiltered': "(from _MAX_ all Babel peer links)",
                    'sInfoPostFix': "",
                    'sSearch': "Filter:"
                }
            });
        });
    });
})(jQuery);
