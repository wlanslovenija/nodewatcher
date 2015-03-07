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
            $.registry.evaluate_rules({});
        });
        $('.registry_form_selector').change(function() {
            $.registry.evaluate_rules({});
        });
        $('.registry_add_item').click(function() {
            $.registry.evaluate_rules({
                append: {
                    registry_id: $(this).data('registry-id'),
                    parent_id: $(this).data('parent')
                }
            });
        });
        $('.registry_remove_item').click(function() {
            $.registry.evaluate_rules({
                remove: {
                    index: $(this).data('index')
                }
            });
        });
    };

    /**
     * Performs server-side rule evaluation based on current values of all
     * entered registry items and executes any sent changes. Server returns
     * changes as a set of Javascript instructions that manipulate the registry
     * object.
     */
    $.registry.evaluate_rules = function(actions) {
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
        });
    };
}));