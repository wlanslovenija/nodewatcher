var registry = {
  // Node identifier that needs to be set
  node_id: '',
  
  // Current evaluation state
  eval_state: {},
  
  /**
   * Performs server-side rule evaluation based on current values of all
   * entered registry items and executes any sent changes. Server returns
   * changes as a set of Javascript instructions that manipulate the registry
   * object. 
   */
  reevaluate_rules: function()
  {
    if (!registry.node_id)
      return;
    
    var forms = $('#registry_forms *').serialize();
    forms += '&STATE=' + encodeURI(JSON.stringify(registry.eval_state));
    $.ajax({
      url: "/registry/evaluate_forms/" + registry.node_id,
      dataType: "html",
      data: forms,
      type: "POST",
      success: function(data) {
        $('#registry_forms').html(data);
      }
    });
  },
  
  /**
   * Initializes the client-side registry functions.
   */
  register_action_fields: function()
  {
    $('.regact_item_chooser').change(function() {
      registry.reevaluate_rules();
    });
    //$('.regact_selector').change(registry.reevaluate_rules);
    $('.regact_adder').click(function() {
      // TODO
    });
    $('.regact_remover').click(function() {
      // TODO
    });
  },
  
  /**
   * Updates the evaluation state that needs to be stored between invocations
   * for proper change handling.
   */
  state: function(new_state)
  {
    registry.eval_state = new_state
  },
};

// Initialize registry functions
$(document).ready(function () {
  registry.register_action_fields();
});

