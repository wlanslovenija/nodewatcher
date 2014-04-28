(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as anonymous module.
        define(['jquery'], factory);
    } else {
        // Browser globals.
        factory(jQuery);
    }
}(function ($) {
    var csrftoken = $.cookie('csrftoken');

    $.postCsrf = function(url, data, success, dataType) {
        return $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: success,
            dataType: dataType,
            crossDomain: false,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });
    };
}));
