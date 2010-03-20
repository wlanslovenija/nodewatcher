/* -*- Mode: JavaScript; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
(function($){
	/**
	 * Clone the table header floating and binds its to the browser scrolling
	 * so that it will be displayed when the original table header is out of sight.
	 *
	 * @param config
	 *		An optional dictionary with configuration for the plugin.
	 *		
	 *		fadeOut		The length of the fade out animation in ms. Default: 250
	 *		faceIn		The length of the face in animation in ms. Default: 250
	 *		floatClass	The class of the div that contains the floating header. The style should
	 *					contain an appropriate z-index value. Default: 'floatHeader'
	 *		cbFadeOut	A callback that is called when the floating header should be faded out.
	 *					The method is called with the wrapped header as argument.
	 *		cbFadeIn	A callback that is called when the floating header should be faded in.
	 *					The method is called with the wrapped header as argument.
	 *
	 * @version 1.1.0
	 * @see http://slackers.se/2009/jquery-floating-header-plugin
	 */
	$.fn.floater = function() {

		
		return this.each(function () {
			var self = $(this);
			var box = self.parent().offset();
			// create the floating container
			self.floatBoxVisible = false;
			self.floatPlaceholder = $('<div style="display:none"></div>');
			self.before(self.floatPlaceholder);

			// Fix for the IE resize handling
			self.IEWindowWidth = document.documentElement.clientWidth;
			self.IEWindowHeight = document.documentElement.clientHeight;
			
			// bind to the scroll event
			$(window).scroll(function() {
				var floatLimit = floatLimit = self.parent().offset().top + self.parent().height();
				var headerOutsideScreen = self.floatBoxVisible ? isHeaderOutsideScreen(self.floatPlaceholder, floatLimit) : isHeaderOutsideScreen(self, floatLimit);
				if (self.floatBoxVisible && !headerOutsideScreen) {		

					self.css({'position': 'static'}); 
					self.floatPlaceholder.css({'display': 'none'}); 
					self.floatBoxVisible = false;

				} else if (headerOutsideScreen) {								
					self.floatBoxVisible = true;
				}
				
				// if the box is visible update the position
				if (self.floatBoxVisible) {
					if ($.browser.msie && $.browser.version == "6.0") {
						// IE6 can't handle fixed positioning; has to use absolute and additional calculation to position correctly.
						self.css({
							'position': 'absolute',
							'top': $(window).scrollTop(),
							'left':  self.offset().left
						}); 
					} else {
						self.css({
							'position': 'fixed',
							'top': 0,
							'left': self.offset().left-$(window).scrollLeft()
						});
					}											
					self.floatPlaceholder.css({'display': 'block', 'width' : self.width(), 'height' : self.height()});
				} 
				 
			});
			
		});
	};
	
	/**
	 * Determines if the element is outside the browser view area.
	 */
	function isHeaderOutsideScreen(element, limit) {
		var top = $(window).scrollTop();
		var y0 = $(element).offset().top;

		return y0 <= top && top <= limit;

	}
})(jQuery);

