var updating = false;
var centering = false;
var visibleNodes = 0;
var shownNodes = {};
var shownNodesNumber = 0;
var shownLinks = [];

var gmap;

function updateStatusbar() {
  var bounds = gmap.getBounds();
  visibleNodes = 0;
  for (var node in shownNodes) {
     if (bounds.containsLatLng(new google.maps.LatLng(shownNodes[node].lat, shownNodes[node].long))) visibleNodes++;
  }
  
  $('#gmap_statusbar').html("Visible " + visibleNodes + " of " + shownNodesNumber + " shown nodes" + (shownNodesNumber != nodes.length ? " (from " + nodes.length + " all nodes)" : ""));
}

function updateNodes(filtersChanged, zoomChanged, moved) {
  if (filtersChanged) {
    gmap.clearOverlays();
    
    shownNodes = {};
    shownNodesNumber = 0;
    shownLinks = [];
    for (var i = 0; i < nodes.length; i++) {
      if ($('#gmap_project_' + nodes[i].project + ':checked').length == 0) continue;
      if ($('#gmap_status_' + nodes[i].status + ':checked').length == 0) continue;
      
      shownNodes[nodes[i].ip] = nodes[i];
      shownNodesNumber++;
      createMarker(nodes[i]);
    }
    
    for (var i = 0; i < links.length; i++) {
      if (shownNodes[links[i].src] && shownNodes[links[i].dst]) {
        shownLinks.push(createLink(shownNodes[links[i].src], shownNodes[links[i].dst], links[i]));
      }
    }
  }
  else if (zoomChanged) {
    var newShownLinks = [];
    for (var i = 0; i < shownLinks.length; i++) {
      gmap.removeOverlay(shownLinks[i].overlay);
      newShownLinks.push(createLink(shownLinks[i].src, shownLinks[i].dst, shownLinks[i].link));
    }
    shownLinks = newShownLinks;
  }
  
  updateStatusbar();
}

function buildHash(lat, long, zoom) {
  var hash = "lat=" + lat + "&long=" + long + "&zoom=" + zoom + "&type=" + gmap.getCurrentMapType().getUrlArg();
  hash += "&project=" + $('input[name="gmap_project"]:checked').map(function () { return $(this).val(); }).get().join(",");
  hash += "&status=" + $('input[name="gmap_status"]:checked').map(function () { return $(this).val(); }).get().join(",");
  return hash;
}

function readHash(hash) {
  var params = {
    "project": [],
    "status": []
  };
  
  if (hash) {
    var splits = hash.split(/&/);
    if (splits.length == 0) {
      udpate_map();
      return;
    }
    
    for (var i = 0; i < splits.length; i++) {
      var sp = splits[i].split(/=/);
      if (sp.length == 2) {
        if (sp[0] == "project") {
          // Values have to be sorted so that they have unique representation (so arraysEqual works properly)
          params.project = $.grep(sp[1].split(/,/), function (el, i) { return $('#gmap_project_' + el).attr('disabled'); }, true).sort();
        }
        else if (sp[0] == "status") {
          // Values have to be sorted so that they have unique representation (so arraysEqual works properly)
          params.status = sp[1].split(/,/).sort();
        }
        else {
          params[sp[0]] = sp[1];
        }
      }
    }
    
    if (params.type) {
      var mapTypes = gmap.getMapTypes();
      for (var m = 0; m < mapTypes.length; m++) {
        if (mapTypes[m].getUrlArg() == params.type) {
          params.type = mapTypes[m];
          break;
        }
      }
    }
  }
  
  return params;
}

function centerMap() {
  var id = $('#gmap_center').val();
  
  if (!id) return;
  
  var bounds = new google.maps.LatLngBounds();
  var count = 0;
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i].project == id) {
      bounds.extend(new google.maps.LatLng(nodes[i].lat, nodes[i].long));
      count++;
    }
  }
  
  // To be robust if user manages to select disabled center map entry
  if (!count) return;
  
  if ($('#gmap_project_' + id + ':checked').length == 0) {
    updating = true;
  
    $('#gmap_project_' + id).attr('checked', 'checked');
  
    updating = false;
  }
  
  $('#gmap_center_default').attr('disabled', 'disabled');
  
  centering = true;
  
  $(window).updatehash(buildHash(bounds.getCenter().lat(), bounds.getCenter().lng(), gmap.getBoundsZoomLevel(bounds)));
  
  centering = false;
}

function updateMap() {
  if (updating) return;
  
  $(window).updatehash(buildHash(gmap.getCenter().lat(), gmap.getCenter().lng(), gmap.getZoom()));
}

function arraysEqual(first, second) {
  if (first.length != second.length) {
    return false;
  }
  for (var i = 0; i < first.length; i++) {
    if (first[i] != second[i]) return false;
  }
  return true;
}

function checkFiltersChanged(currentParams, oldParams) {
  if (arraysEqual(currentParams.project, oldParams.project) && arraysEqual(currentParams.status, oldParams.status)) {
    return false;
  }
  else {
    return true;
  }
}

function checkZoomChanged(currentParams, oldParams) {
  if (oldParams.zoom && (currentParams.zoom == oldParams.zoom)) {
    return false;
  }
  else {
    return true;
  }
}

function checkMoved(currentParams, oldParams) {
  if (oldParams.lat && oldParams.long && (currentParams.lat == oldParams.lat) && (currentParams.long == oldParams.long)) {
    return false;
  }
  else {
    return true;
  }
}

function mapInit(map) {
  gmap = map;
  
  google.maps.Event.addListener(map, "zoomend", function () { updateMap(); });
  google.maps.Event.addListener(map, "moveend", function () { updateMap(); });
  google.maps.Event.addListener(map, "maptypechanged", function () { updateMap(); });
  
  var lock = false;
  google.maps.Event.addListener(map, "move", function () {
    // JS events hopefully execute in one thread so there is no race condition
    // but it also does not really matter if it is
    if (!lock) {
      lock = true;
      // We allow updates to occur at least 100 ms apart
      setTimeout(function () { lock = false; }, 100);
      updateStatusbar();
    }
  });

  $(document).ready(function () {
    $('#gmap_center').change(function () { centerMap(); });
    $('input[name="gmap_project"]').change(function () { updateMap(); });
    $('input[name="gmap_status"]').change(function () { updateMap(); });
    
    $(window).hashchange(function (event, data) {
      var currentHash = data.currentHash;
      var oldHash = data.oldHash;
      
      if (currentHash) {
        var currentParams = readHash(currentHash);
        var oldParams = readHash(oldHash);
        
        if (!currentParams.lat) currentParams.lat = gmap.getCenter().lat();
        if (!currentParams.long) currentParams.long = gmap.getCenter().lng();
        if (!currentParams.zoom) currentParams.zoom = gmap.getZoom();
        if (!currentParams.type) currentParams.type = gmap.getCurrentMapType();
        
        var filtersChanged = checkFiltersChanged(currentParams, oldParams);
        var zoomChanged = checkZoomChanged(currentParams, oldParams);
        var moved = checkMoved(currentParams, oldParams);
        
        if (moved || zoomChanged) {
          if (!centering) {
            $('#gmap_center_default').removeAttr('disabled');
            $('#gmap_center').val("");
          }
        }
        
        updating = true;
        
        gmap.setCenter(new google.maps.LatLng(currentParams.lat, currentParams.long), parseInt(currentParams.zoom), currentParams.type);
        
        $('input[name="gmap_project"]').val(currentParams.project);
        $('input[name="gmap_status"]').val(currentParams.status);
        
        updating = false;
        
        updateNodes(filtersChanged, zoomChanged, moved);
      }
      // We set hash from map state only the first time, if later user deletes/clears hash we do nothing
      // (user could just be going back through history where also an entry with a map URL without hash is
      // and if we set hash again user would be blocked from navigating further back)
      else if (!oldHash) {
        updateMap();
      }
    });
  });
}
