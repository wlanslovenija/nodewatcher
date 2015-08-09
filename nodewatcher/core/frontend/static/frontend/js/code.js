// Common code.

(function ($) {
    $(document).ajaxError(function (event, jqXHR, ajaxSettings, thrownError) {
        // TODO: Handle erros better
        console.error(event, jqXHR, ajaxSettings, thrownError);
    });

	if (!$.nodewatcher) { $.nodewatcher = {}; }
	if (!$.nodewatcher.theme) { $.nodewatcher.theme = {}; }

    $.extend($.nodewatcher.theme, {
    	'iconElement': function(identifier, icons) {
    		if (_.isUndefined(icons)) icons = 'nw';
    		return $('div').addClass('icon ' + icons + ' ' + icons + '-' + identifier).clone().wrap('<i>').parent().html();
    	},
    	'iconHtml': function(identifier, icons) {
    		return $.nodewatcher.theme.iconElement(identifier, icons).clone().wrap('<i>').parent().html();
    	}
    });

})(jQuery);
