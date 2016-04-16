(function ($) {
    var RegistryApiModule = $.extend({}, {
        // Module name.
        name: 'registry',

        _pathToLookup: function (path) {
            var bits = path.split('.');
            bits = $.map(bits, function (bit, j) {
                if ($.isNumeric(bit)) return null;
                // We just skip over the array suffix if it is there.
                return bit.replace(/\[.*\]$/, '');
            });

            registrationPoint = bits.shift();
            registryId = bits.shift().replace(/__/g, '.');
            return [registrationPoint, registryId, bits.join('.')];
        },

        getApiRequestParameters: function (settings, data) {
            var self = this;
            var params = {
                fields: []
            };

            // Setup field projections.
            if (settings.registryFields) {
                $.each(settings.registryFields, function (registrationPoint, fields) {
                    $.each(fields, function (index, field) {
                        var fieldSpecification = [];
                        if ($.isArray(field)) {
                            // Registry identifier and field path.
                            fieldSpecification.push.apply(fieldSpecification, field);
                        } else {
                            // Just registry identifier.
                            fieldSpecification.push(field);
                        }

                        params.fields.push(registrationPoint + ':' + fieldSpecification.join('__'));
                    });
                });
            }

            // Setup filters.
            if (settings.registrySearchField && data.search && data.search.value && data.search.value.length) {
                params[settings.registrySearchField] = data.search.value;
            }

            // Setup ordering.
            var order = data.order || [];
            var ordering = [];
            $.each(order, function (index, orderSpecification) {
                var column = data.columns[orderSpecification.column];
                var lookup = self._pathToLookup(column.data);
                var direction = orderSpecification.dir == 'asc' ? '' : '-';
                // Skip sort by items, which do not specify fields.
                if (!lookup[2].length) return;

                ordering.push(direction + lookup[0] + ':' + lookup[1] + '__' + lookup[2]);
            });
            if (ordering.length) {
                params.ordering = ordering.join(',');
            }

            return params;
        },

        transformApiResponse: function (response) {
            // Transform all dots in registry identifiers to double underscores.
            var results = [];
            $.each(response.results, function (index, result) {
                var transformedResult = {};
                $.each(result, function (registrationPoint, registryItems) {
                    if (registrationPoint[0] == '@' || !$.isPlainObject(registryItems)) {
                        transformedResult[registrationPoint] = registryItems;
                    } else {
                        transformedResult[registrationPoint] = {};
                        $.each(registryItems, function (registryId, value) {
                            transformedResult[registrationPoint][registryId.replace(/\./g, '__')] = value;
                        });
                    }
                });

                results.push(transformedResult);
            });

            response.results = results;
            return response;
        },
    });

    $.nodewatcher.api.registerModule(RegistryApiModule);
})(jQuery);
