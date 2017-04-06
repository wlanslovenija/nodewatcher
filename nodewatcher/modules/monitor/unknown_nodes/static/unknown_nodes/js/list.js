(function ($) {
    function renderTimeAgo(data, type, row, meta) {
        if (type !== 'display')
            return data;

        var t = moment(data);
        if (!t.isValid())
            return "<em>never</em>";

        // TODO: custom date formats, refresing?
        var output = $('<span/>').attr('title', t.format($.nodewatcher.theme.dateFormat)).addClass('time').append(t.fromNow());

        return output.wrap('<span/>').parent().html();
    }

    function renderCertificateSubject(data, type, row, meta) {
        if (type !== 'display')
            return data;

        if (!data)
            return '<em>not provided</em>';

        var output = '';
        if (data.country)
            output += '<span>C=' + data.country + '</span><br/>';
        if (data.locality)
            output += '<span>L=' + data.locality + '</span><br/>';
        if (data.organization)
            output += '<span>O=' + data.organization + '</span><br/>';
        if (data.organizational_unit)
            output += '<span>OU=' + data.organizational_unit + '</span><br/>';

        return output;
    }

    function renderUnknownNodeUuid(table) {
        return function (data, type, row, meta) {
            if (type === 'display') {
                return $('<a/>').attr(
                    'href', $(table).data('register-url-template').replace('{uuid}', data)
                // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                ).text(data).wrap('<span/>').parent().html();
            }
            else {
                return data;
            }
        };
    }

    $(document).ready(function () {
        $('.unknown-node-list').each(function (i, table) {
            $.nodewatcher.api.newDataTable(table, $(table).data('source'), {
                columns: [
                    {data: 'uuid', render: renderUnknownNodeUuid(table)},
                    {data: 'first_seen', render: renderTimeAgo},
                    {data: 'last_seen', render: renderTimeAgo},
                    {data: 'ip_address'},
                    {data: 'certificate.subject.', sortable: false, render: renderCertificateSubject},
                ],
                order: [[0, 'asc']],
                language: {
                    // TODO: Make strings translatable
                    zeroRecords: "No unknown nodes found.",
                    emptyTable: "There are currently no unknown nodes.",
                    info: "_START_ to _END_ of _TOTAL_ unknown nodes shown",
                    infoEmpty: "0 unknown nodes shown",
                    infoFiltered: "(from _MAX_ all unknown nodes)",
                    infoPostFix: "",
                    search: "Filter:"
                }
            });
        });
    });
})(jQuery);
