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

    function renderBuilderUuid(table) {
        return function (data, type, row, meta) {
            if (type === 'display') {
                return $('<a/>').attr(
                    'href', $(table).data('build-url-template').replace('{pk}', data)
                // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML)
                ).text(data).wrap('<span/>').parent().html();
            }
            else {
                return data;
            }
        };
    }

    $(document).ready(function () {
        $('.build-list').each(function (i, table) {
            $.nodewatcher.api.newDataTable(table, $(table).data('source'), {
                registryRoots: {
                    'node': {
                        fields: {
                            'config': [
                                ['core.general', 'name'],
                                ['core.routerid', 'router_id'],
                            ],
                        },
                    },
                },
                columns: [
                    {data: 'uuid', render: renderBuilderUuid(table)},
                    {
                        data: 'node.config.core__general.name',
                        render: $.nodewatcher.api.renderNodeNameSubdocument(table, 'node', true),
                        registry: true,
                    },
                    {data: 'build_channel.name', orderable: false},
                    {data: 'builder.version.name', orderable: false},
                    {data: 'status', render: $.nodewatcher.renderGeneratorResultStatus(table), 'class': 'center', 'width': '20px'},
                    {data: 'created', render: renderTimeAgo},
                    {data: 'node.@id', visible: false},
                    {data: 'node.config.core__routerid[].router_id', visible: false},
                ],
                order: [[5, 'desc']],
                language: {
                    // TODO: Make strings translatable
                    zeroRecords: "No build results found.",
                    emptyTable: "There are currently no build results.",
                    info: "_START_ to _END_ of _TOTAL_ build results shown",
                    infoEmpty: "0 build results shown",
                    infoFiltered: "(from _MAX_ all build results)",
                    infoPostFix: "",
                    search: "Filter:"
                }
            });
        });
    });
})(jQuery);
