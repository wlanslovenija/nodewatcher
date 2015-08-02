
(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    }

    $.extend($.nodewatcher, {

    	'renderStatus' : function (table, category) {
    		return function (data, type, row, meta) {

    			if (data === null) {
    				data = 'None';
    			} else if (data === true) {
    				data = 'True';
    			} else if (data === false) {
    				data = 'False';
    			}

				if (type === 'display') {

					// Attempts to convert text representation to icon if status data is available (provided by the status module)
					if ($.nodewatcher["nodeStatus" + category] && $.nodewatcher["nodeStatus" + category][data]) {

						var status = $.nodewatcher["nodeStatus" + category][data];

						var obj = $('<span />').addClass('icon nw nw-' + status['icon']);

						obj.attr('title', status["description"]);

						return obj.wrap('<span/>').parent().html();

					} else {

						return data;

					}

				} else {
					return data;
				}
			};
    	}

    })

})(jQuery);