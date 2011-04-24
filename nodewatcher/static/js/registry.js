var registry = {
  // Node identifier that needs to be set
  node_id: '',
  
  /**
   * Properly formats dotted registry identifiers.
   *
   * @param reg_class: Registry identifier (like "core.general")
   * @return: Identifier formatted for CSS class name 
   */
  convert_class_name: function(reg_class)
  {
    return reg_class.replace(/\./g, '_');
  },
  
  /**
   * Selects all configuration field variants for some specific registry
   * item class and field name.
   *
   * @param reg_class: Registry identifier (like "core.general")
   * @param field: Field name
   * @param index: Index (needed for classes with multiple items)
   * @return: All fields fitting the above criteria
   */
  field_id_to_fields: function(reg_class, field, index)
  {
    reg_class = reg_class + '_' + field + '_' + index;
    return $('#registry_forms .regfld_' + reg_class);
  },
  
  /**
   * Assigns values to some specific registry item class. The index must
   * already exist.
   *
   * @param reg_class: Registry identifier (like "core.general")
   * @param index: Index (needed for classes with multiple items)
   * @param values: A map of key-value items
   */
  assign: function(reg_class, index, values)
  {
    reg_class = registry.convert_class_name(reg_class);
    $.each(values, function(field, value) {
      registry.field_id_to_fields(reg_class, field, index).val(value);
    });
  },
  
  /**
   * A helper method for returning the counter element for classes with
   * multiple items.
   *
   * @param reg_class: Registry identifier (like "core.general")
   */
  get_counter: function(reg_class)
  {
    return $('#id_reg_' + reg_class + '_sm-form_count')
  },
  
  /**
   * Appends a new registry item to the end of a registry item class that supports
   * multiple items.
   *
   * @param reg_class: Registry identifier (like "core.general")
   * @param values: A map of key-value items
   */
  append: function(reg_class, values)
  {
    reg_class = registry.convert_class_name(reg_class);
    var stub = $('#reg_' + reg_class + '_stub_container');
    if (!stub)
      return;
    
    var counter = registry.get_counter(reg_class);
    var dupe = stub.clone(true);
    var container = $('#reg_' + reg_class + '_mu_container');
    var idx = parseInt(counter.val());
    
    dupe.find('[for],[id],[name],[class]').each(function(_) {
      if ($(this).attr('for'))
        $(this).attr('for', $(this).attr('for').replace('_stub', '_mu_' + idx));
      
      if ($(this).attr('id'))
        $(this).attr('id', $(this).attr('id').replace('_stub', '_mu_' + idx));
      
      if ($(this).attr('name'))
        $(this).attr('name', $(this).attr('name').replace('_stub', '_mu_' + idx));
      
      if ($(this).attr('class'))
        $(this).attr('class', $(this).attr('class').replace('_stub', '_' + idx));
    });
    dupe.attr('id', dupe.attr('id').replace('_stub', '_mu_' + idx));
    dupe.css('display', '');
    
    counter.val(idx + 1);
    container.append(dupe);
    registry.assign(reg_class, idx, values);
  },
  
  /**
   * Removes the last registry item of a registry item class that supports
   * multiple items.
   *
   * @param reg_class: Registry identifier (like "core.general")
   */
  remove: function(reg_class)
  {
    reg_class = registry.convert_class_name(reg_class);
    var counter = registry.get_counter(reg_class);
    if (!counter)
      return;
    
    var idx = parseInt(counter.val()) - 1;
    $('#reg_' + reg_class + '_mu_' + idx + '_container').remove();
    counter.val(idx);
  },
  
  /**
   * Removes all registry items of a registry item class that supports
   * multiple items.
   *
   * @param reg_class: Registry identifier (like "core.general")
   */
  clear_config: function(reg_class)
  {
    reg_class = registry.convert_class_name(reg_class);
    var counter = registry.get_counter(reg_class);
    if (!counter)
      return;
    
    for (var i = 0; i < parseInt(counter.val()); i++) {
      $('#reg_' + reg_class + '_mu_' + i + '_container').remove();
    }
    counter.val(0);
  },
  
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
    
    // TODO some progress notification thingie in the foreground
    var forms = $('#registry_forms *').serialize();
    $.ajax({
      url: "/registry/evaluate_forms/" + registry.node_id,
      dataType: "script",
      data: forms,
      type: "POST",
    });
  },
  
  /**
   * Initializes the client-side registry functions.
   */
  register_action_fields: function()
  {
    $('.regact_selector').change(registry.reevaluate_rules);
    $('.regact_adder').click(function() {
      registry.append($(this).attr('id'), {});
    });
    $('.regact_remover').click(function() {
      registry.remove($(this).attr('id'));
    });
    $('.regact_item_chooser').change(function() {
      var item_subclass = $(this).val();
      var item_class = $(this).attr('id').replace(/id_reg_/, '').replace(/-item/, '');
      var target = $("#reg_" + item_class + "_" + item_subclass);
      
      // Copy shared fields when changing classes
      $('.config_selected.regsct_reg_' + item_class + ' [name]').each(function(_) {
        var field = $(this).attr('name').replace(/^.*?-/, '');
        var value = $(this).val();
        target.find('[name="reg_' + item_class + '_' + item_subclass + '-' + field + '"]').val(value);
      });
      
      $('.config_selected.regsct_reg_' + item_class).removeClass('config_selected').css('display', 'none');
      target.css('display', '').addClass('config_selected');
    });
  },
  
  /**
   * Error handler invoked by the server when something goes wrong with
   * rule evaluation.
   *
   * @param msg: Error message
   */
  error: function(msg)
  {
    // TODO error reports while doing rule evaluation
    alert("ERROR IN RULES ENGINE:\n" + msg);
  },
};

// Initialize registry functions
$(document).ready(function () {
  registry.register_action_fields();
});

