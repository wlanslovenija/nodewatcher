// Common code.

(function ($) {
    $(document).ajaxError(function (event, jqXHR, ajaxSettings, thrownError) {
        // TODO: Handle erros better
        console.error(event, jqXHR, ajaxSettings, thrownError);
    });
})(jQuery);
