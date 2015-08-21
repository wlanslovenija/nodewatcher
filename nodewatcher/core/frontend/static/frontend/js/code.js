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
        'iconElement': function(identifier, icons) {
            if (_.isUndefined(icons)) icons = 'nw';
            return $('<i/>').addClass('icon ' + icons + ' ' + icons + '-' + identifier);
        },
        'iconHtml': function(identifier, icons) {
            return $.nodewatcher.theme.iconElement(identifier, icons).wrap('<div/>').parent().html();
        }
    });

})(jQuery);