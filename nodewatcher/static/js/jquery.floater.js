(function ($) {
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
					// The problem is that there is no easy way to get "auto" CSS value which would be the proper value
					// to copy/set margin-left and margin-right to if defined so in CSS
					if ((self.css('margin-left') == 'auto') || (self.css('margin-right') == 'auto')) {
						// We have a browser which returns "auto", hopefully no work for us
						marginLeft = self.css('margin-left');
						marginRight = self.css('margin-right');
					}
					else if (parseInt(self.css('margin-left')) != 0) {
						// Works in Safari also for "auto" CSS value as it returns computed/current value (offset)
						marginLeft = self.css('margin-left');
						marginRight = "0px";
					}
					else {
						// We calculate offset manually by comparing parent's absolute offset with ours
						marginLeft = self.offset().left - self.parent().offset().left + "px";
						marginRight = "0px";
					}
					self.floatPlaceholder.css({
						'display': 'block',
						'width': self.outerWidth(),
						'height': self.outerHeight(),
						'margin-left': marginLeft,
						'margin-right': marginRight,
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
			return true;
		};
	}
	
	$.fn.floater = function() {
		return this.each(function () {
			var self = $(this);
			self.floatPlaceholder = $('<div />').hide();
			self.before(self.floatPlaceholder);
			$(window).scroll(handleEvent(self));
			$(window).resize(handleEvent(self));
			handleEvent(self)();
		});
	};
})(jQuery);
