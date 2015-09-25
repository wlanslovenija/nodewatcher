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

    function renderBuilderUuid(table) {
        return function (data, type, row, meta) {
            if (type === 'display') {
                return $('<a/>').attr(
                    'href', $(table).data('build-url-template').replace('{pk}', data)
                // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                ).text(data).wrap('<span/>').parent().html();
            }
            else {
                return data;
            }
        };
    }

    $(document).ready(function () {
        $('.build-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    {'data': 'uuid', 'render': renderBuilderUuid(table)},
                    // TODO: How can we generate string from registry, without hardcoding registry relations?
                    {'data': 'node.name', 'render': $.tastypie.nodeSubdocumentName(table, 'node'), 'orderByField': 'node__config_core_generalconfig__name'},
                    {'data': 'build_channel.name'},
                    {'data': 'builder.version.name'},
                    {'data': 'status', 'render': $.nodewatcher.renderGeneratorResultStatus(table), 'class': 'center', 'width': '20px'},
                    {'data': 'created', 'render': renderTimeAgo},
                    // We need extra data to render the node column
                    {'data': 'node.uuid', 'visible': false}
                ],
                // And make default sorting by created column
                'order': [[5, 'desc']],
                'language': {
                    // TODO: Make strings translatable
                    'zeroRecords': "No matching build results found.",
                    'emptyTable ': "There are currently no build results.",
                    'info': "_START_ to _END_ of _TOTAL_ build results shown",
                    'infoEmpty': "0 build results shown",
                    'infoFiltered': "(from _MAX_ all build results)",
                    'infoPostFix': "",
                    'search': "Filter:"
                }
            });
        });
    });
})(jQuery);
