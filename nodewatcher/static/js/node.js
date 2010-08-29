var gmap;
var geocoder;

var autofillNameEnabled;
var autofillMapEnabled;

var streetNumber = /\d+[a-z]*/;
// This format is used also in forms.py so keep it in sync
// We remove all those characters as we are constructing the name by appending the street number ourselves
var nodeName = /[^a-z]/g;

function mapInit(map) {
  gmap = map;
}

function mapEditInit(map) {
  mapInit(map);
  
  var lat = $('#id_geo_lat').val();
  var long = $('#id_geo_long').val();
  
  autofillMapEnabled = !lat && !long;
  autofillNameEnabled = !$('#id_name').val();
  
  if (lat && long) {
    lat = parseFloat(lat);
    long = parseFloat(long);
    if (isFinite(lat) && isFinite(long)) {
      var point = new google.maps.LatLng(lat, long);
      if (point) {
        putMarker(map, point);
        map.setCenter(point);
      }
    }
  }
  
  geocoder = new google.maps.ClientGeocoder();
  geocoder.setViewport(map.getBounds());
}

function mapClick(map, point) {
  autofillMapEnabled = false;
}

function toggleAutoConfiguration() {
  if ($('#id_wan_dhcp').is(':checked')) {
    $('.static_opts').css('display', 'none');
  }
  else {
    $('.static_opts').css('display', '');
  }
}

function toggleImageGeneratorOptions(dontToggleExtAntenna) {
  if ($('#id_template').attr('value') == '') {
    $('.imagegen_opts').css('display', 'none');
  }
  else {
    $('.imagegen_opts').css('display', '');
    toggleAutoConfiguration();
    toggleVpnOptions();
    if (!dontToggleExtAntenna) {
      toggleExtAntenna(true);
    }
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

function toggleDead() {
  if ($('#id_node_type').attr('value') == deadNodeType) {
    $('.alive').css('display', 'none');
    $('#content :input').not('.dead_active :input').attr('disabled', 'disabled');
    clickEnabled = false;
  }
  else {
    $('.alive').css('display', '');
    $('#content :input').removeAttr('disabled');
    toggleIpInput();
    clickEnabled = true;
  }
}

function toggleExtAntenna(dontToggleImageGenerator) {
  if ($('#id_ant_external').is(':checked')) {
    $('.extantenna_opts').css('display', '');
    if (!dontToggleImageGenerator) {
      toggleImageGeneratorOptions(true);
    }
  }
  else {
    $('.extantenna_opts').css('display', 'none');
  }
}

function toggleIpInput() {
  if ($('#id_assign_ip').is(':checked')) {
    $('#id_ip').value = '';
    $('#id_ip').attr('disabled', 'disabled');
  }
  else {
    $('#id_ip').removeAttr('disabled');
  }
}

function updateMapForProject() {
  if (nodeMarker) {
    // marker is already set so we will not move map
    return;
  }
  var projectId = $('#id_project').attr('value');
  if (projects[projectId]) {
    gmap.setCenter(new google.maps.LatLng(projects[projectId].lat, projects[projectId].long), projects[projectId].zoom);
    geocoder.setViewport(gmap.getBounds());
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

function updatePrefixLengthsForPool() {
  if (!pools)
    return;
  
  var projectId = $('#id_project').attr('value');
  var poolId = $('#id_pool').attr('value');
  var pool;
  pool_list = pools[projectId]["list"];
  for (var i = 0; i < pool_list.length; i++) {
    if (pool_list[i].id == poolId) {
      pool = pool_list[i];
      break;
    }
  }
  
  var prefs = $('#id_prefix_len');
  prefs.empty();
  for (var i = pool.min_prefix_len; i <= pool.max_prefix_len; i++) {
    prefs.append('<option value="' + i + '">/' + i + '</option>');
  }
  prefs.attr('value', '' + pool.def_prefix_len);
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

function fillMapLocation() {
  if (($('#id_geo_lat').val() || $('#id_geo_long').val()) && !autofillMapEnabled) {
    return;
  }
  autofillMapEnabled = true;

  geocoder.getLatLng(
    $('#id_location').val(),
    function (point) {
      if (autofillMapEnabled && point && gmap.getBounds().containsLatLng(point)) {
        putMarker(gmap, point);
      }
    }
  );
}

function fillName() {
  if ($('#id_name').val() && !autofillNameEnabled) {
    return;
  }
  autofillNameEnabled = true;

  var name = unidecode($('#id_location').val()).toLowerCase();
  number = name.match(streetNumber);
  name = name.replace(streetNumber, "");
  name = name.replace(nodeName, "");
  if (number) {
    name += "-" + number;
  }
  $('#id_name').val(name);
}

$(document).ready(function () {
  $('#id_project').change(function(event) {
    updateMapForProject();
    updatePoolsForProject();
    
    if ($('#id_prefix_len').length) {
      updatePrefixLengthsForPool();
    }
    return true;
  });
  $('#id_wan_dhcp').change(function(event) { toggleAutoConfiguration(); return true; });
  $('#id_template').change(function(event) { toggleImageGeneratorOptions(); return true; });
  $('#id_node_type').change(function(event) {
    toggleLocation();
    toggleDead();
    return true;
  });
  $('#id_ant_external').change(function(event) { toggleExtAntenna(); return true; });
  $('#id_use_vpn').change(function(event) { toggleVpnOptions(); return true; });
  
  $('#id_location').keyup(function(event) {
    fillMapLocation();
    fillName();
    return true;
  });
  $('#id_geo_lat').change(function(event) { autofillMapEnabled = false; return true; });
  $('#id_geo_long').change(function(event) { autofillMapEnabled = false; return true; });
  $('#id_name').change(function(event) { autofillNameEnabled = false; return true; })
  
  $('#id_root_pass').after(']').after($('<a />').attr('href', '#').text('generate new').click(generateRandomPassword)).after(' [');
    
  toggleAutoConfiguration();
  toggleVpnOptions();
  toggleImageGeneratorOptions();
  toggleLocation();
  toggleExtAntenna();
  updatePoolsForProject();
  toggleDead();
  
  if ($('#id_prefix_len').length) {
    $('#id_pool').change(function(event) {
      updatePrefixLengthsForPool();
      return true;
    });
    
    updatePrefixLengthsForPool();
  }
});
