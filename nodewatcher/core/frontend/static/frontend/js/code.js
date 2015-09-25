// Common code.

(function($) {
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
        // TODO: Handle erros better
        console.error(event, jqXHR, ajaxSettings, thrownError);
    });

    if (!$.nodewatcher) {
        $.nodewatcher = {};
    }
    if (!$.nodewatcher.theme) {
        $.nodewatcher.theme = {};
    }

    $.extend($.nodewatcher.theme, {
        'isIE': /(msie|trident)/i.test(navigator.userAgent) && !window.opera,
        'hasTouch': 'ontouchstart' in document.documentElement,
        'dateFormat' : "MMMM Do YYYY, h:mm:ss a",
        'iconElement': function(identifier, tooltip, icons) {
            if (_.isUndefined(icons)) icons = 'nw';
            var e = $('<i/>').addClass('icon ' + icons + ' ' + icons + '-' + identifier);
            if (!_.isUndefined(tooltip)) e.attr('title', tooltip);
            return e;
        },
        'iconHtml': function(identifier, tooltip, icons) {
            return $.nodewatcher.theme.iconElement(identifier, tooltip, icons).wrap('<div/>').parent().html();
        }
    });

})(jQuery);