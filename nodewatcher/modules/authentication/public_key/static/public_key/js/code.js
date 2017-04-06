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
            $.nodewatcher.api.newDataTable(table, $(table).data('source'), {
                columns: [
                    {data: 'name'},
                    {data: 'fingerprint'},
                    {data: 'created'},
                    {data: null, render: renderActions(table), orderable: false, searchable: false},
                    {data: 'id', visible: false},
                ],
                order: [[0, 'asc']],
                language: {
                    // TODO: Make strings translatable
                    zeroRecords: "No public keys found.",
                    emptyTable: "There are currently no public keys.",
                    info: "_START_ to _END_ of _TOTAL_ public keys shown",
                    infoEmpty: "0 public keys shown",
                    infoFiltered: "(from _MAX_ all public keys)",
                    infoPostFix: "",
                    search: "Filter:"
                }
            });
        });
    });
})(jQuery);
