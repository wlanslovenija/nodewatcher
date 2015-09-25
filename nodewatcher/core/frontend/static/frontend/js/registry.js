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

        $('.registry-simple-mode').bootstrapSwitch({
            size: 'small',
            onSwitchChange: function(event, state) {
                $.registry.update({
                    simple_mode: {
                        value: !state
                    }
                });
            }
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

    function showErrors() {
        // Check if any of the secions in the registry form contains errors and
        // update the class of the menu entry.
        errorsFound = {}
        $('.registry-item-container > legend').each(function(i, section) {
            section = $(section);
            var id = section.attr('id');
            var errors = section.nextUntil('legend').find('.form-group.has-error');
            if (!_.has(errorsFound, id)) {
                errorsFound[id] = 0;
            }
            errorsFound[id] += errors.length;
            errorCount = errorsFound[id]

            if (errorCount > 0) {
                // TODO: Localization.
                var tooltip = errorCount + (errorCount > 1 ? " errors" : " error");

                $('#registry-navbar a[href="#' + id + '"]').addClass('has-error').attr('title', tooltip);
            } else {
                $('#registry-navbar a[href="#' + id + '"]').removeClass('has-error').attr('title', '');
            }

        });
    }

    // Side navigation handling.
    $(window).on('registry:initialize', function(event) {
        // Prepare side navigation.
        $('body').css('position', 'relative').scrollspy({
            target: '#registry-navbar'
        });

        $(window).on('load', function() {
            $('body').scrollspy('refresh')
        });

        // Sidenav affixing.
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

            var $errorsBar = $('.registry-validation-errors');
            $errorsBar.css('width', $('#registry_forms').width());
            $(window).resize(function() {
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

            // Update errors a bit later as well.
            showErrors();
        }, 100);
    });

    $(window).on('registry:update', function(event) {
        $('body').scrollspy('refresh');

        // Update errors.
        showErrors();
    });
}));