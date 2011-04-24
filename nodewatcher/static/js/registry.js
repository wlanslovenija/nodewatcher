registry = {
  // Node identifier that needs to be set
  node_id: '',
  
  convert_class_name: function(reg_class)
  {
    return reg_class.replace(/\./g, '_');
  },
  
  field_id_to_fields: function(reg_class, field, index)
  {
    reg_class = reg_class + '_' + field + '_' + index;
    return $('#registry_forms .regfld_' + reg_class);
  },
  
  assign: function(reg_class, index, values)
  {
    reg_class = registry.convert_class_name(reg_class);
    $.each(values, function(field, value) {
      registry.field_id_to_fields(reg_class, field, index).val(value);
    });
  },
  
  get_counter: function(reg_class)
  {
    return $('#id_reg_' + reg_class + '_sm-form_count')
  },
  
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
  
  register_action_fields: function()
  {
    $('.regact_selector').change(registry.reevaluate_rules);
    $('.regact_adder').click(function() {
      registry.append($(this).attr('id'), {});
    });
    $('.regact_remover').click(function() {
      registry.remove($(this).attr('id'));
    });
  },
  
  error: function(msg)
  {
    // TODO error reports while doing rule evaluation
    alert("ERROR IN RULES ENGINE:\n" + msg);
  },
};

$(document).ready(function () {
  registry.register_action_fields();
});

