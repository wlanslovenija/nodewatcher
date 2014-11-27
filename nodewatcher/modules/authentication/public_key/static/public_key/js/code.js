(function ($) {
    function renderActions(table) {
        return function (data, type, full) {
            if (type != 'display')
                return data;

            return $('<a/>').attr(
                'href', $(table).data('remove-url-template'
            // TODO: Make "remove" string translatable
            // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
            ).replace('{pk}', full.id)).text("remove").wrap('<span/>').parent().html();
        };
    }

    $(document).ready(function () {
        // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
        $('.key-list').each(function (i, table) {
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
                    {'mData': 'name'},
                    {'mData': 'fingerprint'},
                    {'mData': 'created'},
                    {'mData': 'id', 'mRender': renderActions(table), 'bSearchable': false},
                ],
                // And make default sorting by name column
                'aaSorting': [[5, 'desc']],
                'oLanguage': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching public keys found.",
                    'sEmptyTable ': "There are currently no public keys results.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ public keys shown",
                    'sInfoEmpty': "0 public keys shown",
                    'sInfoFiltered': "(from _MAX_ all public keys)",
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
