(function ($) {

	if (!$.nodewatcher) {
        $.nodewatcher = {};
    }
	if (!$.nodewatcher.theme) {
        $.nodewatcher.theme = {};
    }

    $.extend(Highcharts.Chart.prototype, { 
        contextMenu: function (name, items, x, y, width, height) {
            var chart = this,
                navOptions = chart.options.navigation,
                chartWidth = chart.chartWidth,
                chartHeight = chart.chartHeight,
                cacheName = 'cache-' + name,
                wrapper = chart[cacheName],
                menuPadding = Math.max(width, height), // for mouse leave detection
                boxShadow = '3px 3px 10px #888',
                hasTouch = $.nodewatcher.theme.hasTouch,
                hide;
            // create the menu only the first time
            if (!menu) {

                // create a HTML element above the SVG
                chart[cacheName] = wrapper = $('<div />')
                    .appendTo(chart.container)
                    .addClass('btn-group open').css({
                        position: 'absolute',
                        zIndex: 1000,
                        padding: menuPadding + 'px'
                    });

                var menu = $('<ul />')
                    .addClass('dropdown-menu dropdown-right')
                    .appendTo(wrapper);

                // hide on mouse out
                hide = function() {
                    wrapper.removeClass('open');
                };

                menu.on('mouseleave', hide);

                // create the items
                $.each(items, function(i, item) {
                    if (item) {
                        var entry = $('<li/>').addClass('menu-entry').append(
                            $('<a/>').addClass('menu-entry-link').on(
                                hasTouch ? 'touchstart' : 'click', function() {
                                    hide();
                                    item.onclick.apply(chart, arguments);
                                }).html(
                                    item.text || Highcharts.getOptions().lang[item.textKey]))
                                .appendTo(menu);

                    }
                });
                chart.exportMenuWidth = wrapper.offsetWidth;
                chart.exportMenuHeight = wrapper.offsetHeight;
            }

            // if outside right, right align it
            if (x + chart.exportMenuWidth > chartWidth) {
                wrapper.css('right', (chartWidth - x - width - menuPadding));
            } else {
                wrapper.css('left', (x - menuPadding));
            }
            // if outside bottom, bottom align it
            if (y + height + chart.exportMenuHeight > chartHeight) {
                wrapper.css('bottom', (chartHeight - y - menuPadding));
            } else {
                wrapper.css('top', (y + height - menuPadding));
            }

            wrapper.addClass('open');
        },
        addButton: function (options) {
            var chart = this,
                renderer = chart.renderer,
                btnOptions = Highcharts.merge(chart.options.navigation.buttonOptions, options),
                onclick = btnOptions.onclick,
                hasTouch = $.nodewatcher.theme.hasTouch,
                menuItems = btnOptions.menuItems;

            if (btnOptions.enabled === false) {
                return;
            }

            //chart.container.onclick = null;

            var wrapper = $('<div/>').addClass('btn-group export').prependTo(chart.container);

            var button = $('<button data-toggle="dropdown"/>').addClass('btn btn-default dropdown-toggle')
                .append($.nodewatcher.theme.iconElement('cog')).appendTo(wrapper).dropdown();

            var menu = $('<ul />')
                .addClass('dropdown-menu dropdown-right')
                .appendTo(wrapper);

            // add the click event
            if (menuItems) {

                $.each(menuItems, function(i, item) {
                    if (item) {
                        if (item.separator) {
                            var entry = $('<li/>').addClass('divider').appendTo(menu);
                        } else {

                            var entry = $('<li/>').addClass('menu-entry').append(
                                $('<a/>').addClass('menu-entry-link').on(
                                    hasTouch ? 'touchstart' : 'click', function() {
                                        item.onclick.apply(chart, arguments);
                                    }).html(
                                        item.text || Highcharts.getOptions().lang[item.textKey]))
                                    .appendTo(menu);
                        }
                    }
                });
            }
        }
    });

})(jQuery);
