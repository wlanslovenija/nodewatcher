var gmap;

function mapInit(map) {
  gmap = map;
}

function toggleAutoConfiguration() {
  if ($('#id_wan_dhcp').is(':checked')) {
    $('.static_opts').css('display', 'none');
  }
  else {
    $('.static_opts').css('display', '');
  }
}

function toggleImageGeneratorOptions() {
  if ($('#id_template').attr('value') == '') {
    $('.imagegen_opts').css('display', 'none');
  }
  else {
    $('.imagegen_opts').css('display', '');
    toggleAutoConfiguration();
  }
}

function toggleVpnOptions() {
  if ($('#id_use_vpn').is(':checked')) {
    $('.vpn_opts').css('display', '');
  }
  else {
    $('.vpn_opts').css('display', 'none');
  }
}

function toggleLocation() {
  if ($('#id_node_type').attr('value') == mobileNodeType) {
    $('.location_opts').css('display', 'none');
  }
  else {
    $('.location_opts').css('display', '');
  }
}

function toggleExtAntenna() {
  if ($('#id_ant_external').is(':checked')) {
    $('.extantenna_opts').css('display', '');
  }
  else {
    $('.extantenna_opts').css('display', 'none');
  }
}

function toggleIpInput() {
  if ($('#id_assign_ip').is(':checked')) {
    $('#id_ip').value = '';
    $('#id_ip').attr('disabled', 'disabled');
    $('.assign_subnet').css('display', 'none');
  }
  else {
    $('#id_ip').removeAttr('disabled');
    $('.assign_subnet').css('display', '');
  }
}

function updateMapForProject() {
  var projectId = $('#id_project').attr('value');
  for (var i = 0; i < projects.length; i++) {
    if (projectId == projects[i].id) {
      gmap.setCenter(new google.maps.LatLng(projects[i].lat, projects[i].long), projects[i].zoom);
      return;
    }
  }
}

function updatePoolsForProject() {
  if (!pools)
    return;
  
  var projectId = $('#id_project').attr('value');
  var pool = $('#id_pool');
  pool.empty();
  
  pool_list = pools[projectId]["list"];
  for (var i = 0; i < pool_list.length; i++) {
    pool.append('<option value="' + pool_list[i].id + '">' + pool_list[i].description + ' [' + pool_list[i].subnet + ']</option>');
  }
  
  pool.attr('value', pools[projectId]["default"]);
}

function generateRandomPassword(event) {
  event.preventDefault();
  var choices = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  var password = "";
  for (var i = 0; i < 8; i++) {
    password += choices.charAt(Math.floor(Math.random() * choices.length));
  }
  $('#id_root_pass').val(password);
  return false;
}

$(document).ready(function () {
  $('#id_project').change(function(event) { updateMapForProject(); updatePoolsForProject(); });
  $('#id_wan_dhcp').change(function(event) { toggleAutoConfiguration(); });
  $('#id_template').change(function(event) { toggleImageGeneratorOptions(); });
  $('#id_node_type').change(function(event) { toggleLocation(); });
  $('#id_ant_external').change(function(event) { toggleExtAntenna(); });
  $('#id_use_vpn').change(function(event) { toggleVpnOptions(); });
  
  $('#id_root_pass').after(']').after($('<a />').attr('href', '#').text('generate new').click(generateRandomPassword)).after(' [');
  
  toggleAutoConfiguration();
  toggleVpnOptions();
  toggleImageGeneratorOptions();
  toggleLocation();
  toggleExtAntenna();
  updatePoolsForProject();
});
