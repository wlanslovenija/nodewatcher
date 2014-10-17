(function ($) {
    function renderBuilderUuid(table) {
        return function (data, type, full) {
            if (type === 'display') {
                return $('<a/>').attr(
                    'href', $(table).data('build-url-template'
                // TODO: Make "unknown" string translatable
                // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                ).replace('{pk}', full.uuid)).text(data || "unknown").wrap('<span/>').parent().html();
            }
            else {
                // TODO: Make "unknown" string translatable
                return data || "unknown";
            }
        };
    }

    $(document).ready(function () {
        // TODO: Enable Ajax caching, see http://datatables.net/forums/discussion/18899/make-cache-false-in-ajax-request-optional
        $('.build-list').each(function (i, table) {
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
                    {'mData': 'uuid', 'mRender': renderBuilderUuid(table)},
                    {'mData': 'node.name', 'bSortable': false},
                    {'mData': 'build_channel.name'},
                    {'mData': 'builder.version.name'},
                    {'mData': 'status'},
                    {'mData': 'created'},
                ],
                // And make default sorting by name column
                'aaSorting': [[5, 'desc']],
                'oLanguage': {
                    // TODO: Make strings translatable
                    'sZeroRecords': "No matching build results found.",
                    'sEmptyTable ': "There are currently no build results.",
                    'sInfo': "_START_ to _END_ of _TOTAL_ build results shown",
                    'sInfoEmpty': "0 build results shown",
                    'sInfoFiltered': "(from _MAX_ all build results)",
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
