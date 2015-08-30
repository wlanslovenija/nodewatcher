(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as anonymous module.
        define(['jquery'], factory);
    } else {
        // Browser globals.
        factory(jQuery);
    }
}(function ($) {
    var regpoint_id;
    var root_id;
    var updating = false;

    // Registry methods object
    $.registry = {};

    /**
     * Initializes the registry API.
     *
     * @param rpid Registry point identifier
     * @param rid Root object identifier
     */
    $.registry.initialize = function(rpid, rid) {
        regpoint_id = rpid;
        root_id = rid;

        // Bind event handlers
        $('.registry_form_item_chooser').change(function() {
            $.registry.update({});
        });
        $('.registry_form_selector').change(function() {
            $.registry.update({});
        });
        $('input[type="checkbox"]').change(function() {
            $.registry.update({});
        });
        $('.registry_add_item').click(function() {
            $.registry.update({
                append: {
                    registry_id: $(this).data('registry-id'),
                    parent_id: $(this).data('parent')
                }
            });
        });
        $('.registry_remove_item').click(function() {
            $.registry.update({
                remove: {
                    index: $(this).data('index')
                }
            });
        });

        $('.registry-defaults-enable').click(function() {
            $.registry.update({
                defaults: {
                    value: true
                }
            });
        });
        $('.registry-defaults-disable').click(function() {
            $.registry.update({
                defaults: {
                    value: false
                }
            });
        });

        $(window).trigger('registry:initialize');

    };

    /**
     * Performs server-side rule evaluation based on current values of all
     * entered registry items and executes any sent changes. Server returns
     * changes as a set of Javascript instructions that manipulate the registry
     * object.
     */
    $.registry.update = function(actions) {
        // Ignore multiple parallel updates as they may cause transaction deadlocks.
        if (updating) {
            return;
        }
        updating = true;

        // Prepare form in serialized form (pun intended)
        var forms = $('#registry_forms *').serialize();
        forms += '&ACTIONS=' + encodeURI(JSON.stringify(actions));

        $.postCsrf(
            "/registry/evaluate_forms/" + regpoint_id + "/" + root_id,
            forms
        ).done(function(data) {
            $('#registry_forms').html(data);

            /* Ensure that on-load event handlers get called again. */
            var event;

            if (document.createEvent) {
                event = document.createEvent("HTMLEvents");
                event.initEvent("load", true, true);
            } else {
                event = document.createEventObject();
                event.eventType = "load";
            }

            event.eventName = "load";

            if (document.createEvent) {
                window.dispatchEvent(event);
            } else {
                window.fireEvent("on" + event.eventType, event);
            }

            $(window).trigger('registry:update');

            updating = false;
        });
    };
}));