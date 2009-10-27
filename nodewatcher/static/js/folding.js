
$(document).ready(function () {

	$("[id$=folder]").each(function(o) {

		var id = $(this).attr("id");

		if (id == null || id.length < 6)
			return;

		var object = $("#" + id.substring(0, id.length - 6) + "foldee")

		if (object == null)
			return;

		if ($(this).hasClass("closed")) {
			object.addClass("closed");
			object.hide();
		} else object.removeClass("closed");

		$(this).click(function() {
			object.slideToggle(400);
			object.toggleClass("closed");
			$(this).toggleClass("closed");
		});

	});
} );


