(function ($) {
  $.fn.addAnchor = function(title) {
    title = title || "Link here";
    return this.filter("*[id]").each(function() {
      if ($(this).text()) {
        $("<a class='anchor'> \u00B6</a>").attr("href", "#" + this.id).attr("title", title).appendTo(this);
      }
      else {
        $(this).wrap($("<a />").attr("href", "#" + this.id).attr("title", title));
      }
    });
  }
})(jQuery);

$(document).ready(function () {
  $("#content").find("h1,h2,h3,h4,h5,h6").addAnchor("Link to this section");
  $(".graph img").addAnchor("Link to this graph");
});
