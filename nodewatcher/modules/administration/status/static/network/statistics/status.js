(function ($) {
    $(document).ready(function () {
        return $.ajax({
            'dataType': 'json',
            'url': $('#statistics-nodes-by-status').data('url'),
            // We don't use global jQuery Ajax setting to not conflict with some other code,
            // but we make sure we use traditional query params serialization for all our requests.
            'traditional': true
        }).done(function (data) {
            var series = [];

            _.each(data.results, function(point) {
                series.push({
                    name: point.status.verbose_name,
                    icon: point.status.icon,
                    y: point.nodes
                });
            });

            // Create the plot.
            $('#statistics-nodes-by-status').highcharts({
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
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                            style: {
                                color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                            },
                            connectorColor: 'silver'
                        }
                    }
                },
                series: [{
                    // TODO: Translate.
                    name: "Nodes",
                    data: series
                }]
            });
        });
    });
})(jQuery);
