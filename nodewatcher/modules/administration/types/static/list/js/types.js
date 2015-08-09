
(function ($) {
    if (!$.nodewatcher) {
        $.nodewatcher = {};
    }

    $.extend($.nodewatcher, {

    	'renderNodeType' : function (table) {
    		return function (data, type, row, meta) {

				if (type === 'display') {

					// Attempts to convert text representation to icon if status data is available (provided by the status module)
					if ($.nodewatcher["nodeType"] && $.nodewatcher["nodeType"][data]) {

						var ntype = $.nodewatcher["nodeType"][data];

						var obj = $('<span />').addClass('icon nw nw-' + ntype['icon']);

						obj.attr('title', ntype["name"]);

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