(function ($) {
    function nodeNames(table) {
        return function (data, type, full) {
            if (type === 'display') {
                return $.map(data, function (node, i) {
                    return $('<a/>').attr(
                        'href', $(table).data('node-url-template'
                    // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                    // TODO: Make string translatable
                    ).replace('{pk}', node.uuid)).text(node.name || "unknown").wrap('<span/>').parent().html();
                }).join(", ");
            }
            else {
                return $.map(data, function (node, i) {
                    // TODO: Make string translatable
                    return node.name || "unknown";
                }).join(" ");
            }
        };
    }

    function fnServerParams(aoData) {
        var match = null;
        var columns = [];
        var sorting = [];
        var search = null;
        var columnSearch = [];
        for (var i = 0; i < aoData.length; i++) {
            switch (aoData[i].name) {
                case 'iDisplayStart':
                    aoData[i].name = 'offset';
                    break;
                case 'iDisplayLength':
                    aoData[i].name = 'limit';
                    break;
                case (match = aoData[i].name.match(/^mDataProp_(\d+)$/) || {}).input:
                    // We store the mapping, but then remove it from
                    // aoData below by falling through the switch
                    columns[match[1]] = aoData[i].value;
                    match = null;
                case (match = aoData[i].name.match(/^iSortCol_(\d+)$/) || {}).input:
                    if (match) {
                        // We store the sorting column, but then remove it
                        // from aoData below by falling through the switch
                        if (!sorting[match[1]]) sorting[match[1]] = {};
                        sorting[match[1]].column = aoData[i].value;
                        match = null;
                    }
                case (match = aoData[i].name.match(/^sSortDir_(\d+)$/) || {}).input:
                    if (match) {
                        // We store the sorting direction, but then remove it
                        // from aoData below by falling through the switch
                        if (!sorting[match[1]]) sorting[match[1]] = {};
                        sorting[match[1]].direction = aoData[i].value;
                        match = null;
                    }
                case (match = aoData[i].name.match(/^sSearch_(\d+)$/) || {}).input:
                    if (match) {
                        // We store the column search, but then remove it
                        // from aoData below by falling through the switch
                        columnSearch[match[1]] = aoData[i].value;
                        match = null;
                    }
                case 'sSearch':
                    if (aoData[i].name === 'sSearch') {
                        // We store the global search, but then remove it
                        // from aoData below by falling through the switch
                        search = aoData[i].value;
                    }
                case 'iColumns':
                case 'sColumns':
                case 'iSortingCols':
                case (aoData[i].name.match(/^bRegex/) || {}).input:
                case (aoData[i].name.match(/^bSortable/) || {}).input:
                case (aoData[i].name.match(/^bSearchable/) || {}).input:
                    aoData.splice(i, 1);
                    i--;
                    break;
                default:
                    break;
            }
        }
        $.each(sorting, function (i, sort) {
            var s = sort.direction === 'desc' ? '-' : '';
            var bits = columns[sort.column].split('.');
            s += $.map(bits, function (bit, j) {
                if ($.isNumeric(bit)) return null;
                return bit;
            }).join('__');
            aoData.push({
                'name': 'order_by',
                'value': s
            })
        });
        $.each(columnSearch, function (i, search) {
            if (!search) return;
            aoData.push({
                'name': columns[i] + '__icontains',
                'value': search
            })
        });
        if (search) {
            aoData.push({
                'name': 'filter',
                'value': search
            });
        }
    }

    function fnServerData(sSource, aoData, fnCallback, oSettings) {
        // Instead of passing sEcho to the server and breaking caching, we set
        // it in JavaScript, which still makes clear to dataTables which request
        // is returning and when, but does not modify HTTP request
        var echo = null;
        for (var i = 0; i < aoData.length; i++) {
            switch (aoData[i].name) {
                case 'sEcho':
                    echo = aoData[i].value;
                    aoData.splice(i, 1);
                    i--;
                    break;
                default:
                    break;
            }
        }
        $.fn.dataTable.defaults.fnServerData(sSource, aoData, function (json) {
            json.sEcho = echo;
            json.iTotalRecords = json.meta.nonfiltered_count;
            json.iTotalDisplayRecords = json.meta.total_count;
            fnCallback(json);
        }, oSettings);
    }

    $(document).ready(function () {
        $('.events-list').each(function (i, table) {
            $(table).dataTable({
                'bProcessing': true,
                'bPaginate': true,
                'sPaginationType': 'full_numbers',
                'iDisplayLength': 50,
                'bLengthChange': false,
                'bFilter': true,
                'bSort': true,
                'bInfo': true,
                'bAutoWidth': true,
                // TODO: Use our own state saving by changing URL anchor
                'bStateSave': false,
                'bServerSide': true,
                'fnServerParams': fnServerParams,
                'fnServerData': fnServerData,
                'sAjaxSource': $(table).data('source'),
                'sAjaxDataProp': 'objects',
                // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
                'sDom': 'ifprtifp',
                'aoColumns': [
                    {'mData': 'timestamp'},
                    {'mData': 'related_nodes', 'mRender': nodeNames(table)},
                    {'mData': 'title'}
                ],
                'aaSorting': [[0, 'desc']],
                'oLanguage': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching events found.",
                    'sEmptyTable ': "There are currently no events recorded.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ events shown",
                    'sInfoEmpty': "0 events shown",
                    'sInfoFiltered': "(from _MAX_ all events)",
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
