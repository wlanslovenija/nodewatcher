(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    }
    if (!$.nodewatcher.api) {
        $.nodewatcher.api = {};
    }

    // Module registrations.
    var apiModules = [];

    $.extend($.nodewatcher.api, {
        newDataTable: function (table, ajaxUrl, options) {
            var $table = $(table).dataTable($.extend({
                'processing': true,
                'paging': true,
                'pagingType': 'full_numbers',
                'pageLength': 50,
                // Set to "ifrtif" if pagination (page buttons) are not wanted, set to "ifprtifp" if pagination is wanted.
                'dom': 'ifprtifp',
                'lengthChange': false,
                'searching': true,
                'ordering': true,
                'info': true,
                'autoWidth': true,
                // TODO: Use our own state saving by changing URL anchor.
                'stateSave': false,
                'serverSide': true,
                'ajax': {
                    'url': ajaxUrl,
                    'data': $.nodewatcher.api._createDataTablesApiRequest(table),
                    'dataSrc': 'results',
                    'cache': true,
                    'traditional': true
                },
                'search': {
                    // Initial search string.
                    'search': '',
                    // We pass strings to the server side as they are.
                    'regex': true,
                    'smart': false
                }
            }, options)).on('xhr.dt', $.nodewatcher.api._processDataTablesApiResponse(table));
            var api = $table.api();
            // TODO: Link processing pop-up position to be linked with header's position.
            var fixedHeader = new $.fn.dataTable.FixedHeader(api);
            return $table;
        },

        /**
         * Converts dataTables server-side parameters to API parameters.
         */
        _createDataTablesApiRequest: function (table) {
            return function (data, settings) {
                var params = {};

                // Handle limit and offset.
                if ('length' in data) {
                    // In nodewatcher API, max limit is set with limit=0, but dataTables uses -1.
                    if (data.length === -1) {
                        params.limit = 0;
                    } else {
                        params.limit = data.length;
                    }
                }

                if ('start' in data) {
                    params.offset = data.start;
                }

                // Allow modules to augment the request based on table configuration.
                var settings = $(table).dataTable().api().init();
                $.extend(params, $.nodewatcher.api.getApiRequestParameters(settings, data));

                return params;
            };
        },

        /**
         * Processes API response from the server and transforms it for
         * consumption by DataTables.
         */
        _processDataTablesApiResponse: function (table) {
            return function (event, settings, data, jqXHR, context) {
                if (data) {
                    data.recordsTotal = data.count;
                    data.recordsFiltered = data.count;
                }

                data = $.nodewatcher.api.transformApiResponse(data);
            };
        },

        /**
         * Returns API request parameters. Modules can hook into this discovery by providing
         * a `getApiRequestParameters` method.
         *
         * @param {Object} settings Table configuration
         * @param {Object} data Current request information
         * @return {Object} API request parameters
         */
        getApiRequestParameters: function (settings, data) {
            var params = {};
            this.callModules('getApiRequestParameters', settings, data, function (result) {
                $.extend(params, result || {});
            });
            return params;
        },

        /**
         * Transforms the given API response. Modules can hook into this transformation by
         * providing a `transformApiResponse` method.
         *
         * @param {Object} response Response received from the server
         */
        transformApiResponse: function (response) {
            this.callModules('transformApiResponse', response, function (result) {
                $.extend(response, result || {});
            });
            return response;
        },

        /**
         * Calls a method on all registered modules and collects the results. If the last
         * argument is a function, then it is called with each module's result. All other
         * arguments are passed to the method unchanged.
         *
         * @param {string} methodName Method name
         */
        callModules: function (methodName) {
            var methodArguments = Array.from(arguments);
            var resultHandler = $.isFunction(methodArguments[methodArguments.length - 1]) ? methodArguments.pop() : function () {};
            methodArguments.shift();

            $.each(apiModules, function (index, module) {
                if ($.isFunction(module[methodName])) {
                    resultHandler(module[methodName].apply(module, methodArguments));
                }
            });
        },

        /**
         * Registers a new API module.
         *
         * @param {Object} module A module instance
         */
        registerModule: function (module) {
            apiModules.push(module);
        },

        /**
         * Uses top-level object's @id for a link.
         */
        renderNodeName: function (table) {
            return function (data, type, row, meta) {
                if (type === 'display') {
                    return $('<a/>').attr(
                        'href', $(table).data('node-url-template').replace('{pk}', row['@id'])
                    // TODO: Make "unknown" string translatable.
                    // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML).
                    ).text(data || "unknown").wrap('<span/>').parent().html();
                } else {
                    // TODO: Make "unknown" string translatable.
                    return data || "unknown";
                }
            };
        },

        /**
         * Uses subdocument @id for a link (or links). If nodeField is specified, it
         * will use that row field instead of current data.
         */
        renderNodeNameSubdocument: function (table, nodeField, routerId) {
            return function (data, type, row, meta) {
                if (nodeField) {
                    data = row[nodeField];
                }
                if (!$.isArray(data)) {
                    data = [data];
                }
                if (type === 'display') {
                    return $.map(data, function (node, i) {
                        var name = $('<a/>').attr(
                            'href', $(table).data('node-url-template').replace('{pk}', node['@id'])
                        // TODO: Make "unknown" string translatable.
                        // A bit of jQuery mingling to get outer HTML ($.html() returns inner HTML).
                        ).text(node.name || "unknown").wrap('<span/>').parent().html();
                        if (routerId && node.router_id) {
                            var router_ids = $.map(node.router_id, function (item) { return item.router_id; });
                            if (router_ids.length > 0) {
                                name += ' <span class="small">(' + router_ids.join(', ') + ')</a>';
                            }
                        }
                        return name;
                    }).join(", ");
                } else {
                    return $.map(data, function (node, i) {
                        // TODO: Make "unknown" string translatable.
                        return node.name || "unknown";
                    }).join(" ");
                }
            };
        },
    });
})(jQuery);
