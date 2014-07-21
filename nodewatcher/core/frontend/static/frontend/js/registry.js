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
        $('.registry_form_adder').click(function() {
            $.registry.evaluate_rules({ 'append' : $(this).attr('name') });
        });
        $('.registry_form_remover').click(function() {
            $.registry.evaluate_rules({ 'remove_last' : $(this).attr('name') });
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
        });
    };
}));