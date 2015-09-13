(function($) {

	function showErrors() {
		// Check if any of the secions in the registry form contains errors and 
		// update the class of the menu entry
		$('#registry_forms > legend').each(function(i, section) {
			section = $(section);
			var id = section.attr('id');
			var errors = section.nextUntil('legend').find('.form-group.has-error');

			if (errors.length > 0) {

				// TODO: localization
				var tooltip = errors.length + (errors.length > 1 ? " errors" : " error");
				
				$('#registry-navbar a[href="#' + id + '"]').addClass('has-error').attr('title', tooltip);

			} else {

				$('#registry-navbar a[href="#' + id + '"]').removeClass('has-error').attr('title', '');

			}

		});
	}

	$(window).on('registry:initialize', function(event) {

		// Prepare side navigation
		$('body').css('position', 'relative').scrollspy({
			target: '#registry-navbar'
		});

		$(window).on('load', function() {
			$('body').scrollspy('refresh')
		});

		// Sidenav affixing
		setTimeout(function() {
			var $sideBar = $('#registry-navbar')

			$sideBar.affix({
				offset: {
					top: function() {
						var offsetTop = $('#registry_forms').offset().top;
						return (this.top = offsetTop);
					},
					bottom: 10
				}
			});

			var $errorsBar = $('#registry_forms > .errors')

			$errorsBar.css('width', $('#registry_forms').width());

			$( window ).resize(function() {
				$errorsBar.css('width', $('#registry_forms').width());
			});

			$errorsBar.affix({
				offset: {
					top: function() {
						var offsetTop = $errorsBar.offset().top;
						return (this.top = offsetTop);
					},
					bottom: 10
				}
			});

			// Update errors a bit later as well
			showErrors();
		}, 100);

		
	});

	$(window).on('registry:update', function(event) {

		$('body').scrollspy('refresh');

		// Update errors
		showErrors();

	});

})(jQuery);