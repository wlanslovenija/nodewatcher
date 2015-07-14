(function ($) {
    function renderActions(table) {
        return function (data, type, row, meta) {
            if (type === 'display') {
                return $('<a/>').attr(
                    'href', $(table).data('remove-url-template').replace('{pk}', row.id)
                // TODO: Make "remove" string translatable
                // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                ).text("remove").wrap('<span/>').parent().html();
            }
            else {
                return data;
            }
        };
    }

    $(document).ready(function () {
        $('.key-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    {'data': 'name'},
                    {'data': 'fingerprint'},
                    {'data': 'created'},
                    {'data': null, 'render': renderActions(table), 'orderable': false, 'searchable': false},
                    {'data': 'id', 'visible': false}
                ],
                // And make default sorting by name column
                'order': [[0, 'asc']],
                'language': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching public keys found.",
                    'sEmptyTable ': "There are currently no public keys.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ public keys shown",
                    'sInfoEmpty': "0 public keys shown",
                    'sInfoFiltered': "(from _MAX_ all public keys)",
                    'sInfoPostFix': "",
                    'sSearch': "Filter:"
                }
            });
        });
    });
})(jQuery);
