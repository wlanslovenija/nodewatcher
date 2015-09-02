(function ($) {

	if (!$.nodewatcher) {
        $.nodewatcher = {};
    }
	if (!$.nodewatcher.theme) {
        $.nodewatcher.theme = {};
    }

    $.extend(Highcharts.Chart.prototype, {
        contextMenu: function (name, menuItems) {
            var chart = this,
                navOptions = chart.options.navigation,
                chartWidth = chart.chartWidth,
                chartHeight = chart.chartHeight,
                cacheName = 'cache-' + name,
                menu = chart[cacheName],
                hasTouch = $.nodewatcher.theme.hasTouch;
            // create the menu only the first time
            if (menu.is(':empty')) {
                // create the items
                $.each(menuItems, function(i, item) {
                    if (item) {
                        if (item.separator) {
                            $('<li/>').addClass('divider').appendTo(menu);
                        } else {
                            $('<li/>').addClass('menu-entry').appendTo(menu).append(
                                $('<a/>').addClass('menu-entry-link').on(
                                    hasTouch ? 'touchstart' : 'click', function() {
                                        item.onclick.apply(chart, arguments);
                                    }).html(
                                        item.text || Highcharts.getOptions().lang[item.textKey]));
                                    
                        }
                    }
                });
            }

        },

        // TODO: This function should use contextMenu so that it is extensible by plugins.
        // TODO: Menu should not pass through mouseover events because then tooltips are shown below (which makes it impossible to print a chart without a tooltip).
        addButton: function (options) {
            var chart = this,
                renderer = chart.renderer,
                btnOptions = Highcharts.merge(chart.options.navigation.buttonOptions, options),
                hasTouch = $.nodewatcher.theme.hasTouch;

            if (btnOptions.enabled === false) {
                return;
            }

            $(chart.renderTo).addClass("chart");

            var wrapper = $('<div/>').addClass('btn-group export').prependTo(chart.renderTo).bind('mouseenter', function(ev) { ev.stopPropagation(); });

            var button = $('<button data-toggle="dropdown"/>').addClass('btn btn-default dropdown-toggle')
                .append($.nodewatcher.theme.iconElement('cog')).appendTo(wrapper).dropdown();

            chart['cache-export-menu'] = $('<ul />')
                .addClass('dropdown-menu dropdown-right')
                .appendTo(wrapper);//.bind('mouseenter', function(ev) { ev.stopPropagation(); });

            wrapper.on('show.bs.dropdown', function () {
                chart.contextMenu('export-menu', btnOptions.menuItems);
            });

        }
    });

})(jQuery);
