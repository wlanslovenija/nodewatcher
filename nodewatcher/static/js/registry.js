var registry = {
  // Regpoint identifier that needs to be set
  regpoint_id: '',
  
  // Regpoint root identifier that needs to be set
  root_id: '',
  
  /**
   * Performs server-side rule evaluation based on current values of all
   * entered registry items and executes any sent changes. Server returns
   * changes as a set of Javascript instructions that manipulate the registry
   * object. 
   */
  reevaluate_rules: function(actions)
  {
    // Prepare form in serialized form (pun intended)
    var forms = $('#registry_forms *').serialize();
    forms += '&ACTIONS=' + encodeURI(JSON.stringify(actions));
    
    // Disable the form and display a nifty dialog
    $('#registry_forms *').attr('disabled', 'disabled');
    $('#reg_loading_dialog').dialog('open');
    
    $.ajax({
      url: "/registry/evaluate_forms/" + registry.regpoint_id + "/" + registry.root_id,
      dataType: "html",
      data: forms,
      type: "POST",
      timeout: 10000,
      success: function(data) {
        $('#reg_loading_dialog').dialog('close');
        $('#registry_forms').html(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        // TODO handle errors, give the option to retry
        alert('errrror! ' + textStatus + ' ' + errorThrown);
      },
    });
  },
  
  /**
   * Initializes the client-side registry functions.
   */
  register_action_fields: function()
  {
    // Initialize the dialog widget
    $('#reg_loading_dialog').dialog({
      autoOpen: false,
      resizable: false,
      closeOnEscape: false
    });
    
    // Bind event handlers
    $('.regact_item_chooser').change(function() {
      registry.reevaluate_rules({});
    });
    $('.regact_selector').change(function() {
      registry.reevaluate_rules({});
    });
    $('.regact_adder').click(function() {
      registry.reevaluate_rules({ 'append' : $(this).attr('name') })
    });
    $('.regact_remover').click(function() {
      registry.reevaluate_rules({ 'remove_last' : $(this).attr('name') })
    });
  },
  
  /**
   * Updates the evaluation state that needs to be stored between invocations
   * for proper change handling.
   */
  state: function(new_state)
  {
    $('#reg_eval_state').val(new_state);
  },
};

// Initialize registry functions
$(document).ready(function () {
  registry.register_action_fields();
});

