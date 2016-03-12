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

        // Bind event handlers.
        $('input[type="checkbox"]').change(function() {
            $.registry.update({});
        });
        $('select').change(function() {
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

    var loadingDialog = (function () {
        var div = $(
            '<div class="modal fade nw-dialog" id="registryLoadingDialog" tabindex="-1" ' +
                'role="dialog" aria-hidden="true" data-backdrop="static">' +
                '<div class="modal-dialog modal-sm">' +
                    '<div class="modal-content">' +
                        '<div class="modal-header">' +
                            '<h4 class="modal-title">' +
                                'Updating configuration' +
                            '</h4>' +
                            '<span class="small">' +
                                'Your changes are being applied, please wait.' +
                            '</span>' +
                        '</div>' +
                        '<div class="modal-body">' +
                            '<div class="progress">' +
                                '<div class="progress-bar progress-bar-info ' +
                                'progress-bar-striped active" ' +
                                'style="width: 100%">' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
        return {
            show: function() {
                div.modal();
            },
            hide: function () {
                div.modal('hide');
            },

        };
    })();

    var errorDialog = (function () {
        var div = $(
            '<div class="modal fade nw-dialog type-danger" id="registryErrorDialog" tabindex="-1" ' +
                'role="dialog" aria-hidden="true" data-backdrop="static">' +
                '<div class="modal-dialog modal-lg">' +
                    '<div class="modal-content">' +
                        '<div class="modal-header">' +
                            '<h4 class="modal-title">' +
                                'Configuration failed' +
                            '</h4>' +
                        '</div>' +
                        '<div class="modal-body">' +
                            '<p>' +
                                'There was an error while applying configuration, which usually ' +
                                'indicates a problem in one of the configuration modules.' +
                            '</p>' +
                            '<p>' +
                                'Please contact the site administrator.' +
                            '</p>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
        return {
            show: function() {
                div.modal();
            },
            hide: function () {
                div.modal('hide');
            },

        };
    })();

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
        loadingDialog.show();

        // Prepare form in serialized form (pun intended)
        var forms = $('#registry_forms *').serialize();
        forms += '&ACTIONS=' + encodeURI(JSON.stringify(actions));

        $.postCsrf(
            // TODO: Dynamically resolve the URL and do not have it hard-coded.
            "/registry/evaluate_forms/" + regpoint_id + "/" + root_id + "/",
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
            loadingDialog.hide();
        }).fail(function() {
            updating = false;
            loadingDialog.hide();
            errorDialog.show();
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