
(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    }

    $.extend($.nodewatcher, {

    	'renderGeneratorResultStatus' : function (table, category) {
    		return function (data, type, row, meta) {

    			if (data === null) {
    				data = 'None';
    			} else if (data === true) {
    				data = 'True';
    			} else if (data === false) {
    				data = 'False';
    			}

				if (type === 'display') {

    				return $.nodewatcher.theme.iconHtml('generator-' + data, data);

				} else {
					return data;
				}
			};
    	}

    })

})(jQuery);