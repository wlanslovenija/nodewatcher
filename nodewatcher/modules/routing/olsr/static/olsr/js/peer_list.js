(function ($) {
    function renderTimeAgo(data, type, row, meta) {
        if (type !== 'display')
            return data;

        var t = moment(data);
        if (!t.isValid())
            return "<em>never</em>";

        // TODO: custom date formats, refresing?
        var output = $('<span/>').attr('title', t.format($.nodewatcher.theme.dateFormat)).append(t.fromNow());

        return output.wrap('<span/>').parent().html();

    }

    $(document).ready(function () {
        $('.olsr-peer-list').each(function (i, table) {
            $.nodewatcher.api.newDataTable(table, $(table).data('source'), {
                registryRoots: {
                    'peer': {
                        fields: {
                            'config': [
                                ['core.general', 'name'],
                                ['core.routerid', 'router_id'],
                            ],
                        },
                    },
                },
                columns: [
                    {
                        data: 'peer.config.core__general.name',
                        render: $.nodewatcher.api.renderNodeNameSubdocument(table, 'peer', true),
                        registry: true,
                    },
                    {data: 'last_seen', render: renderTimeAgo},
                    {data: 'lq'},
                    {data: 'ilq'},
                    {data: 'etx'},
                    {data: 'peer.@id', visible: false},
                    {data: 'peer.config.core__routerid[].router_id', visible: false},
                ],
                order: [[0, 'asc']],
                paging: false,
                language: {
                    // TODO: Make strings translatable
                    zeroRecords: "No OLSR peer links found.",
                    emptyTable: "There are currently no OLSR peer links.",
                    info: "_START_ to _END_ of _TOTAL_ OLSR peer links shown",
                    infoEmpty: "0 OLSR peer links shown",
                    infoFiltered: "(from _MAX_ all OLSR peer links)",
                    infoPostFix: "",
                    search: "Filter:"
                }
            });
        });
    });
})(jQuery);
