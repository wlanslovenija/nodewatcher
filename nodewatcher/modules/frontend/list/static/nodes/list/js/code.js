(function ($) {
    function groupDrawCallback(table) {
        return function (oSettings) {
            if (oSettings.aiDisplay.length == 0) {
                return;
            }

            var trs = $(table).find('tbody tr');
            var colspan = trs.eq(0).find('td').length;
            var lastGroup = null;
            trs.each(function (i, tr) {
                var displayIndex = oSettings._iDisplayStart + i;
                var group = oSettings.aoData[oSettings.aiDisplay[displayIndex]]._aData[oSettings.aoColumns[0].mData];
                if (group !== lastGroup) {
                    $('<tr />').addClass('group').append(
                        $('<td />').attr('colspan', colspan).html(group)
                    ).insertBefore($(tr));
                    lastGroup = group;
                }
            });
        };
    }

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

    function nodeName(table) {
        return function (data, type, full) {
            if (type !== 'display') return data;

            return $('<a/>').attr(
                'href', $(table).data('node-url-template'
            // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
            // TODO: Make string translatable
            ).replace('{pk}', full.uuid)).text(data || "unknown").wrap('<span/>').parent().html();
        };
    }

    $(document).ready(function () {
        $('.node-list').each(function (i, table) {
            $(table).dataTable({
                'bProcessing': true,
                'bPaginate': false,
                'bLengthChange': false,
                'bFilter': true,
                'bSort': true,
                'bInfo': true,
                'bAutoWidth': true,
                // TODO: Use our own state saving by changing URL anchor
                'bStateSave': false,
                // TODO: Start using bServerSide and move limit there?
                'sAjaxSource': $(table).data('source') + '?limit=5000',
                'sAjaxDataProp': 'objects',
                // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
                'sDom': 'ifrtif',
                'aoColumns': [
                    {'mData': 'type', 'bVisible': false},
                    {'mData': 'name', 'mRender': nodeName(table)},
                    {'mData': 'last_seen'},
                    {'mData': 'status.network', 'mRender': iconFromLegend('network')},
                    // Not really reasonable to be searchable
                    {'mData': 'status.monitored', 'mRender': iconFromLegend('monitored'), 'bSearchable': false},
                    {'mData': 'status.health', 'mRender': iconFromLegend('health')},
                    {'mData': 'project'}
                ],
                // Grouping, we fix sorting by (hidden) type column
                'aaSortingFixed': [[0, 'asc']],
                // And make default sorting by name column
                'aaSorting': [[1, 'asc']],
                'fnDrawCallback': groupDrawCallback(table),
                'oLanguage': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching nodes found.",
                    'sEmptyTable ': "There are currently no nodes registered/connected.",
                    // We do not provide pagination here, so we use only __TOTAL__ here
                    'sInfo': "_TOTAL_ nodes shown",
                    'sInfoEmpty': "0 nodes shown",
                    'sInfoFiltered': "(from _MAX_ all nodes)",
                    'sInfoPostFix': "",
                    'sSearch': "Filter:"
                },
                'oSearch': {
                    // Initial search string
                    'sSearch': '',
                    // We support regex
                    'bEscapeRegex': false
                }
            });
        });
    });
})(jQuery);
