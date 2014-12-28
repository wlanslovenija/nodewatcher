(function ($) {
    function iconFromLegend(legendName) {
        return function (data, type, full) {
            if (type !== 'display') return data;

            switch (data) {
                case true: data = 'True'; break;
                case false: data = 'False'; break;
                case null: data = 'None'; break;
                default: break;
            }

            return $('.node-list-legend .' + legendName + '-status dt.' + data).html();
        };
    }

    $(document).ready(function () {
        // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
        $('.node-list').each(function (i, table) {
            $(table).dataTable({
                'bProcessing': true,
                'bPaginate': false,
                'sPaginationType': 'full_numbers',
                'iDisplayLength': 5000,
                'bLengthChange': false,
                'bFilter': true,
                'bSort': true,
                'bInfo': true,
                'bAutoWidth': true,
                // TODO: Use our own state saving by changing URL anchor
                'bStateSave': false,
                'bServerSide': true,
                'fnServerParams': $.tastypie.fnServerParams,
                'fnServerData': $.tastypie.fnServerData,
                'sAjaxSource': $(table).data('source'),
                'sAjaxDataProp': 'objects',
                // Set to "ifprtifp" if pagination is enabled, set to "ifrtif" if disabled
                'sDom': 'ifrtif',
                'aoColumns': [
                    {'mData': 'type', 'bVisible': false},
                    {'mData': 'name', 'mRender': $.tastypie.nodeName(table)},
                    {'mData': 'last_seen'},
                    {'mData': 'status.network', 'mRender': iconFromLegend('network')},
                    {'mData': 'status.monitored', 'mRender': iconFromLegend('monitored')},
                    {'mData': 'status.health', 'mRender': iconFromLegend('health')},
                    {'mData': 'project'},
                    {'mData': 'uuid', 'bVisible': false}
                ],
                // Grouping, we fix sorting by (hidden) type column
                'aaSortingFixed': [[0, 'asc']],
                // And make default sorting by name column
                'aaSorting': [[1, 'asc']],
                'fnDrawCallback': $.tastypie.groupDrawCallback(table),
                'oLanguage': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching nodes found.",
                    'sEmptyTable ': "There are currently no nodes recorded/connected.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ nodes shown",
                    'sInfoEmpty': "0 nodes shown",
                    'sInfoFiltered': "(from _MAX_ all nodes)",
                    'sInfoPostFix': "",
                    'sSearch': "Filter:"
                },
                'oSearch': {
                    // Initial search string
                    'sSearch': '',
                    // We pass strings to the server side as they are
                    'bEscapeRegex': false
                }
            });
        });
    });
})(jQuery);
