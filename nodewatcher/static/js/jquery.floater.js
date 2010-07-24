(function($) {
	function isOutsideWindow(element, limit) {
		var top = $(window).scrollTop();
		var y0 = $(element).offset().top;
		return y0 <= top && top <= limit;
	}
	
	function handleEvent(self) {
		return function () {
			var visible = self.floatPlaceholder.is(':visible');
			var floatLimit = self.parent().offset().top + self.parent().height();
			var outsideWindow = visible ? isOutsideWindow(self.floatPlaceholder, floatLimit) : isOutsideWindow(self, floatLimit);
			if (visible && !outsideWindow) {		
				self.css({'position': 'static'}); 
				self.floatPlaceholder.css({'display': 'none'}); 
				visible = false;
			}
			else if (outsideWindow) {
				if (!visible) {
					self.floatPlaceholder.css({
						'display': 'block',
						'width': self.outerWidth(),
						'height': self.outerHeight(),
						// The problem is that there is no easy way to get "auto" CSS value which would be the proper value
						// to set margin-left and margin-right to (as it is currently defined in our CSS so)
						// Reading margin-left gives offset in Safari and position().left in Firefox, together they work, but for how long?
						'margin-left': parseInt(self.css('margin-left')) + self.position().left + "px",
						'margin-top': self.css('margin-top'),
						'margin-bottom': self.css('margin-bottom')
					});					
				}
				visible = true;
			}
			if (visible) {
				self.css({
					'position': 'fixed',
					'top': 0,
					'left': self.floatPlaceholder.offset().left - $(window).scrollLeft()
				});
			}
		};
	}
	
	$.fn.floater = function() {
		return this.each(function () {
			var self = $(this);
			self.floatPlaceholder = $('<div />').hide();
			self.before(self.floatPlaceholder);
			$(window).scroll(handleEvent(self));
			$(window).resize(handleEvent(self));
		});
	};
})(jQuery);
