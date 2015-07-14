(function ($) {
    $(document).ready(function () {
        $('.node-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    {'data': 'type', 'visible': false},
                    {'data': 'name', 'render': $.tastypie.nodeNameRender(table)},
                    {'data': 'last_seen'},
                    {'data': 'status.network'},
                    {'data': 'status.monitored'},
                    {'data': 'status.health'},
                    {'data': 'project'},
                    // So that user can search by UUID
                    {'data': 'uuid', 'visible': false}
                ],
                // Grouping, we fix sorting by (hidden) type column
                'orderFixed': [[0, 'asc']],
                // And make default sorting by name column
                'order': [[1, 'asc']],
                'drawCallback': $.tastypie.groupDrawCallback(table),
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
