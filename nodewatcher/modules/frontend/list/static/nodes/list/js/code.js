(function ($) {
    $(document).ready(function () {
        $('.node-list').each(function (i, table) {
            $(table).dataTable({
                'processing': true,
                'paging': true,
                'pagingType': 'full_numbers',
                // We effectively disable pagination by specifying large page length
                // Additionally, we hide pages buttons themselves below
                'pageLength': 5000,
                // Set to "ifrtif" if pagination (page buttons) are not wanted, set to "ifprtifp" if pagination is wanted
                'dom': 'ifrtif',
                'lengthChange': false,
                'searching': true,
                'ordering': true,
                'info': true,
                'autoWidth': true,
                // TODO: Use our own state saving by changing URL anchor
                'stateSave': false,
                'serverSide': true,
                'ajax': {
                    'url': $(table).data('source'),
                    'data': $.tastypie.ajaxData(table),
                    'dataSrc': 'objects',
                    'cache': true,
                    'traditional': true
                },
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
                },
                'search': {
                    // Initial search string
                    'search': '',
                    // We pass strings to the server side as they are
                    'regex': true,
                    'smart': false
                }
            }).on('xhr.dt', $.tastypie.xhrCallback(table));
        });
    });
})(jQuery);
