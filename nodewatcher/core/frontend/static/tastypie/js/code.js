(function ($) {
    if (!$.tastypie) {
        $.tastypie = {};
    }

    function pathToRelation(path) {
        var bits = path.split('.');
        return $.map(bits, function (bit, j) {
            if ($.isNumeric(bit)) return null;
            return bit;
        }).join('__');
    }

    $.extend($.tastypie, {
        // Uses top-level object's uuid for a link
        'nodeName': function (table) {
            return function (data, type, full) {
                if (type === 'display') {
                    return $('<a/>').attr(
                        'href', $(table).data('node-url-template'
                    // TODO: Make "unknown" string translatable
                    // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                    ).replace('{pk}', full.uuid)).text(data || "unknown").wrap('<span/>').parent().html();
                }
                else {
                    // TODO: Make "unknown" string translatable
                    return data || "unknown";
                }
            };
        },

        // Uses subdocument uuid for a link (or links)
        'nodeSubdocumentName': function (table) {
            return function (data, type, full) {
                if (!$.isArray(data)) {
                    data = [data];
                }
                if (type === 'display') {
                    return $.map(data, function (node, i) {
                        return $('<a/>').attr(
                            'href', $(table).data('node-url-template'
                        // TODO: Make "unknown" string translatable
                        // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                        ).replace('{pk}', node.uuid)).text(node.name || "unknown").wrap('<span/>').parent().html();
                    }).join(", ");
                }
                else {
                    return $.map(data, function (node, i) {
                        // TODO: Make "unknown" string translatable
                        return node.name || "unknown";
                    }).join(" ");
                }
            };
        },

        'fnServerParams': function (aoData) {
            var match = null;
            var columns = [];
            var sorting = [];
            var search = null;
            var columnSearch = [];
            for (var i in aoData) {
                switch (i) {
                    case 'iDisplayStart':
                        aoData[i].name = 'offset';
                        break;
                    case 'iDisplayLength':
                        aoData[i].name = 'limit';
                        // In Tastypie, max limit is set with limit=0, but dataTables uses -1
                        if (aoData[i].value === -1) {
                            aoData[i].value = 0;
                        }
                        break;
                    case (match = i.match(/^mDataProp_(\d+)$/) || {}).input:
                        // We store the mapping, but then remove it from
                        // aoData below by falling through the switch
                        columns[match[1]] = aoData[i].value;
                        match = null;
                    case (match = i.match(/^iSortCol_(\d+)$/) || {}).input:
                        if (match) {
                            // We store the sorting column, but then remove it
                            // from aoData below by falling through the switch
                            if (!sorting[match[1]]) sorting[match[1]] = {};
                            sorting[match[1]].column = aoData[i].value;
                            match = null;
                        }
                    case (match = i.match(/^sSortDir_(\d+)$/) || {}).input:
                        if (match) {
                            // We store the sorting direction, but then remove it
                            // from aoData below by falling through the switch
                            if (!sorting[match[1]]) sorting[match[1]] = {};
                            sorting[match[1]].direction = aoData[i].value;
                            match = null;
                        }
                    case (match = i.match(/^sSearch_(\d+)$/) || {}).input:
                        if (match) {
                            // We store the column search, but then remove it
                            // from aoData below by falling through the switch
                            columnSearch[match[1]] = aoData[i].value;
                            match = null;
                        }
                    case 'sSearch':
                        if (i === 'sSearch') {
                            // We store the global search, but then remove it
                            // from aoData below by falling through the switch
                            search = aoData[i].value;
                        }
                    case 'iColumns':
                    case 'sColumns':
                    case 'iSortingCols':
                    case (i.match(/^bRegex/) || {}).input:
                    case (i.match(/^bSortable/) || {}).input:
                    case (i.match(/^bSearchable/) || {}).input:
                        aoData.splice(i, 1);
                        i--;
                        break;
                    default:
                        break;
                }
            }
            $.each(columns, function (i, column) {
                aoData.push({
                    'name': 'fields',
                    'value': pathToRelation(column)
                })
            });
            $.each(sorting, function (i, sort) {
                var s = sort.direction === 'desc' ? '-' : '';
                s += pathToRelation(columns[sort.column]);
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
        },

        'serverData': function (aoData) {
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


            return aoData;
//console.log(oSettings);
            /*$.ajax(sSource, {'data' : aoData, 'success' : function (json) {
                json.sEcho = echo;
                // nonfiltered_count is our addition to Tastypie for better integration with dataTables
                json.iTotalRecords = json.meta.nonfiltered_count;
                json.iTotalDisplayRecords = json.meta.total_count;
console.log(json);
                fnCallback(json);
            }});*/

        },

        'fnServerData': function (sSource, aoData, fnCallback, oSettings) {
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
                // nonfiltered_count is our addition to Tastypie for better integration with dataTables
                json.iTotalRecords = json.meta.nonfiltered_count;
                json.iTotalDisplayRecords = json.meta.total_count;
                fnCallback(json);
            }, oSettings);

        },

        // Groups rows based on the first column (you have to use 'aaSortingFixed': [[0, 'asc']]
        // to fix ordering primarily to the first column)
        'groupDrawCallback': function (table) {
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
    });
})(jQuery);
