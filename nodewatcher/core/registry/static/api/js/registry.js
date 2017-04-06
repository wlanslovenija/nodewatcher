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
            var params = {};

            if (!settings.registryRoots) return {};

            $.each(settings.registryRoots, function (rootField, rootSettings) {
                var fieldsAttribute = 'fields';
                var filtersAttribute = 'filters';
                var orderingAttribute = 'ordering';
                if (rootField !== '*') {
                    fieldsAttribute = rootField + '__' + fieldsAttribute;
                    filtersAttribute = rootField + '__' + filtersAttribute;
                    orderingAttribute = rootField + '__' + orderingAttribute;
                }

                // Setup field projections.
                params[fieldsAttribute] = [];
                $.each(rootSettings.fields, function (registrationPoint, fields) {
                    $.each(fields, function (index, field) {
                        var fieldSpecification = [];
                        if ($.isArray(field)) {
                            // Registry identifier and field path.
                            fieldSpecification.push.apply(fieldSpecification, field);
                        } else {
                            // Just registry identifier.
                            fieldSpecification.push(field);
                        }

                        params[fieldsAttribute].push(registrationPoint + ':' + fieldSpecification.join('__'));
                    });
                });

                // Setup filters.
                if (rootSettings.searchFilters && data.search && data.search.value && data.search.value.length) {
                    params[filtersAttribute] = rootSettings.searchFilters.replace(/%s/g, data.search.value);
                }

                // Setup ordering.
                var order = data.order || [];
                var ordering = [];
                var nonRegistryOrdering = [];
                $.each(order, function (index, orderSpecification) {
                    var column = settings.columns[orderSpecification.column];
                    var direction = orderSpecification.dir == 'asc' ? '' : '-';

                    if (column.registry) {
                        var lookup = self._pathToLookup(column.data);
                        // Skip sort by items, which do not specify fields.
                        if (!lookup[2].length) return;

                        ordering.push(direction + lookup[0] + ':' + lookup[1] + '__' + lookup[2]);
                    } else {
                        // Non-registry order.
                        nonRegistryOrdering.push(direction + column.data.replace(/\./g, '__'));
                    }
                });
                if (ordering.length) {
                    params[orderingAttribute] = ordering.join(',');
                }
                if (nonRegistryOrdering.length) {
                    if (orderingAttribute === 'ordering') {
                        params['ordering'] += ',';
                    } else {
                        params['ordering'] = '';
                    }

                    params['ordering'] += nonRegistryOrdering.join(',');
                }
            });

            return params;
        },

        transformApiResponse: function (settings, response) {
            if (!settings.registryRoots) return response;

            function transformRootField(rootField) {
                if ($.isArray(rootField)) {
                    return $.map(rootField, transformRootField);
                }

                var transformedResult = {};
                $.each(rootField, function (registrationPoint, registryItems) {
                    if (registrationPoint[0] == '@' || !$.isPlainObject(registryItems)) {
                        transformedResult[registrationPoint] = registryItems;
                    } else {
                        transformedResult[registrationPoint] = {};
                        $.each(registryItems, function (registryId, value) {
                            transformedResult[registrationPoint][registryId.replace(/\./g, '__')] = value;
                        });
                    }
                });

                return transformedResult;
            }

            var results = [];
            $.each(settings.registryRoots, function (rootField, rootSettings) {
                // Transform all dots in registry identifiers to double underscores.
                $.each(response.results, function (index, result) {
                    var transformedResult = {};
                    if (rootField === '*') {
                        transformedResult = transformRootField(result);
                    } else {
                        $.each(result, function (key, value) {
                            if (key === rootField) {
                                transformedResult[key] = transformRootField(value);
                            } else {
                                // Copy all other fields.
                                transformedResult[key] = value;
                            }
                        });
                    }

                    results.push(transformedResult);
                });
            });

            response.results = results;
            return response;
        },
    });

    $.nodewatcher.api.registerModule(RegistryApiModule);
})(jQuery);
