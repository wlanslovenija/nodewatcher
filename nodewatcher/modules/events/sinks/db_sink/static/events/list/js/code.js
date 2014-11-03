(function ($) {
    $(document).ready(function () {
        // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
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
                'fnServerParams': $.tastypie.fnServerParams,
                'fnServerData': $.tastypie.fnServerData,
                'sAjaxSource': $(table).data('source'),
                'sAjaxDataProp': 'objects',
                // Set to "ifprtifp" if pagination is enabled, set to "ifrtif" if disabled
                'sDom': 'ifprtifp',
                'aoColumns': [
                    {'mData': 'timestamp'},
                    {'mData': 'related_nodes', 'mRender': $.tastypie.nodeSubdocumentName(table)},
                    {'mData': 'description'}
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
