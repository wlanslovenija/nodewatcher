(function ($) {
    $(document).ready(function () {
        return $.ajax({
            'dataType': 'json',
            'url': $('#statistics-nodes-by-project').data('url'),
            // We don't use global jQuery Ajax setting to not conflict with some other code,
            // but we make sure we use traditional query params serialization for all our requests.
            'traditional': true
        }).done(function (data) {
            var series = [];

            _.each(data.statistics, function(point) {
                series.push({
                    name: point.project,
                    y: point.count
                });
            });

            // Create the plot.
            $('#statistics-nodes-by-project').highcharts({
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
