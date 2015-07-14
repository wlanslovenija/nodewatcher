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
        'nodeNameRender': function (table) {
            return function (data, type, row, meta) {
                if (type === 'display') {
                    return $('<a/>').attr(
                        'href', $(table).data('node-url-template'
                    // TODO: Make "unknown" string translatable
                    // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                    ).replace('{pk}', row.uuid)).text(data || "unknown").wrap('<span/>').parent().html();
                }
                else {
                    // TODO: Make "unknown" string translatable
                    return data || "unknown";
                }
            };
        },

        // Uses subdocument uuid for a link (or links)
        'nodeSubdocumentName': function (table) {
            return function (data, type, row, meta) {
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

        // Converts dataTables server-side parameters to Tastypie parameters
        'ajaxData': function (table) {
            return function (data, settings) {
                var tastypieParams = {
                    'order_by': [],
                    'fields': []
                };

                if ('length' in data) {
                    // In Tastypie, max limit is set with limit=0, but dataTables uses -1
                    if (data.length === -1) {
                        tastypieParams.length = 0;
                    }
                    else {
                        tastypieParams.limit = data.length;
                    }
                }

                if ('start' in data) {
                    tastypieParams.offset = data.start;
                }

                if (data.search && data.search.value && data.search.value.length) {
                    tastypieParams.filter = data.search.value;
                }

                var columns = data.columns || [];
                for (var i = 0; i < columns.length; i++) {
                    var path = pathToRelation(columns[i].data);
                    tastypieParams.fields.push(path);
                    if (columns[i].search && columns[i].search.value && columns[i].search.value.length) {
                        tastypieParams[path + '__icontains'] = columns[i].search.value;
                    }
                }

                var order = data.order || [];
                for (var i = 0; i < order.length; i++) {
                    var s = order[i].dir === 'desc' ? '-' : '';
                    s += pathToRelation(columns[order[i].column].data);
                    tastypieParams.order_by.push(s);
                }

                return tastypieParams;
            };
        },

        // Processes data returned from the server before dataTables processes it
        'xhrCallback': function (table) {
            return function (event, settings, data, jqXHR, context) {
                if (data.meta) {
                    // "nonfiltered_count" is our addition to Tastypie for better integration with dataTables
                    data.recordsTotal = data.meta.nonfiltered_count;
                    data.recordsFiltered = data.meta.total_count;
                }
            };
        },

        // Groups rows based on the first column (you have to use 'orderFixed': [[0, 'asc']]
        // to fix ordering primarily to the first column). Based on
        // https://datatables.net/examples/advanced_init/row_grouping.html
        'groupDrawCallback': function (table) {
            return function (settings) {
                var api = this.api();
                var rows = api.rows({page: 'current'}).nodes();
                var $rows = $(rows);
                var lastGroup = null;
                var colspan = $rows.eq(0).find('td').length;

                api.column(0, {page: 'current'}).data().each(function (group, i) {
                    if (lastGroup !== group) {
                        $('<tr />').addClass('group').append(
                            $('<td />').attr('colspan', colspan).html(group)
                        ).insertBefore($rows.eq(i));
                        lastGroup = group;
                    }
                });
            };
        }
    });
})(jQuery);
