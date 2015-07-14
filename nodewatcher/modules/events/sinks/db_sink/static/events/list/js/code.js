(function ($) {
    $(document).ready(function () {
        $('.events-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'pageLength': 50,
                'dom': 'ifprtifp',
                'columns': [
                    {'data': 'timestamp'},
                    // TODO: Correctly render names and links
                    {'data': 'related_nodes', 'render': $.tastypie.nodeSubdocumentName(table)},
                    {'data': 'description'},
                    // We need extra data to render the related nodes column
                    {'data': 'related_nodes.name', 'visible': false},
                    {'data': 'related_nodes.uuid', 'visible': false}
                ],
                'aaSorting': [[0, 'desc']],
                'language': {
                    // TODO: Make strings translatable
                    'zeroRecords': "No matching events found.",
                    'emptyTable ': "There are currently no events.",
                    'info': "_START_ to _END_ of _TOTAL_ events shown",
                    'infoEmpty': "0 events shown",
                    'infoFiltered': "(from _MAX_ all events)",
                    'infoPostFix': "",
                    'search': "Filter:"
                }
            });
        });
    });
})(jQuery);
