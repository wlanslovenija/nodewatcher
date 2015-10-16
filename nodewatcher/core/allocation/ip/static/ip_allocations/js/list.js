(function ($) {
    $(document).ready(function () {
        $('.ip-allocation-list').each(function (i, table) {
            $.tastypie.newDataTable(table, $(table).data('source'), {
                'columns': [
                    {'data': 'pool.description'},
                    {'data': 'family'},
                    {'data': 'network'},
                    {'data': 'prefix_length'}
                ],
                'order': [[2, 'asc']],
                'language': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No IP allocations found.",
                    'sEmptyTable ': "There are currently no IP allocations.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ IP allocations shown",
                    'sInfoEmpty': "0 IP allocations shown",
                    'sInfoFiltered': "(from _MAX_ all IP allocations)",
                    'sInfoPostFix': "",
                    'sSearch': "Filter:"
                }
            });
        });
    });
})(jQuery);
