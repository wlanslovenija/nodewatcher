(function ($) {
    $(document).ready(function () {
        return $.ajax({
            'dataType': 'json',
            'url': $('#statistics-nodes-by-device').data('url'),
            // We don't use global jQuery Ajax setting to not conflict with some other code,
            // but we make sure we use traditional query params serialization for all our requests.
            'traditional': true
        }).done(function (data) {
            var manufacturers = {};
            var colors = Highcharts.getOptions().colors;
            var colorIndex = 0;

            _.each(data.results, function (point) {
                if (!point.device) {
                    point.device = {
                        // TODO: Translate.
                        manufacturer: "Unknown",
                        model: "Unknown"
                    }
                }

                if (!manufacturers[point.device.manufacturer]) {
                    manufacturers[point.device.manufacturer] = {
                        count: 0,
                        models: [],
                        color: colors[colorIndex++],
                    }
                }

                var manufacturer = manufacturers[point.device.manufacturer];
                manufacturer.count += point.nodes;
                manufacturer.models.push(_.extend({count: point.nodes}, point.device));
            });

            var manufacturersSeries = [];
            var modelsSeries = [];

            _.each(manufacturers, function (data, manufacturer) {
                manufacturersSeries.push({
                    name: manufacturer,
                    y: data.count,
                    color: data.color
                });

                _.each(data.models, function (model, index) {
                    var brightness = 0.2 - (index / data.models.length) / 5;
                    modelsSeries.push({
                        name: model.model,
                        y: model.count,
                        color: Highcharts.Color(data.color).brighten(brightness).get()
                    });
                });
            });

            // Create the plot.
            $('#statistics-nodes-by-device').highcharts({
                chart: {
                    type: 'pie',
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false
                },
                credits: {
                    enabled: false
                },
                title: {
                    text: ""
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        tooltip: {
                            // TODO: Translate.
                            pointFormat: '<span style="color:{point.color}">\u25CF</span> Nodes: <b>{point.y}</b><br/>'
                        }
                    }
                },
                series: [
                    {
                        // TODO: Translate.
                        name: "Manufacturers",
                        data: manufacturersSeries,
                        size: '60%',
                        dataLabels: {
                            formatter: function () {
                                return this.percentage > 5 ? this.point.name : null;
                            },
                            color: '#ffffff',
                            distance: -30
                        }
                    },
                    {
                        // TODO: Translate.
                        name: "Models",
                        data: modelsSeries,
                        size: '80%',
                        innerSize: '60%',
                        dataLabels: {
                            formatter: function () {
                                // display only if larger than 1
                                return this.percentage > 1 ? '<b>' + this.point.name + ':</b> ' + this.percentage.toFixed(2) + '%' : null;
                            }
                        }
                    }
                ]
            });
        });
    });
})(jQuery);
