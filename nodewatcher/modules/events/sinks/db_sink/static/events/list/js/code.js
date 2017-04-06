(function($) {
    function renderDate(data, type, row, meta) {
        if (type !== 'display')
            return data;

        var t = moment(data);
        if (!t.isValid())
            return "<em>unknown</em>";

        return t.format($.nodewatcher.theme.dateFormat);
    }

    $(document).ready(function() {
        $('.events-list').each(function(i, table) {
            $.nodewatcher.api.newDataTable(table, $(table).data('source'), {
                registryRoots: {
                    'related_nodes': {
                        fields: {
                            'config': [
                                ['core.general', 'name'],
                                ['core.routerid', 'router_id'],
                            ],
                        },
                    },
                },
                columns: [
                    {data: 'timestamp', render: renderDate},
                    {
                        data: 'related_nodes.config.core__general.name',
                        render: $.nodewatcher.api.renderNodeNameSubdocument(table, 'related_nodes', true),
                        registry: true,
                    },
                    {data: 'description', orderable: false},
                ],
                order: [[0, 'desc']],
                language: {
                    // TODO: Make strings translatable
                    zeroRecords: "No events found.",
                    emptyTable: "There are currently no events.",
                    info: "_START_ to _END_ of _TOTAL_ events shown",
                    infoEmpty: "0 events shown",
                    infoFiltered: "(from _MAX_ all events)",
                    infoPostFix: "",
                    search: "Filter:"
                }
            });
        });
    });
})(jQuery);