$(document).ready(function () {
	$(".folding").each(function (i) {
		var ul = $(this).next();
		if ($(this).hasClass("closed")) {
			ul.addClass("closed").hide();
		}
		else {
			ul.removeClass("closed");
		}
		$(this).click(function () {
			ul.slideToggle(400).toggleClass("closed");
			$(this).toggleClass("closed");
		});
	});
});
