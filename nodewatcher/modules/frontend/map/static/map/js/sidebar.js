//Add nodes to the map sidebar table
function sidebarTableAddNode(node,table){
    var sidebarTable  = document.getElementById(String(table));

    var sidebarTableRow = document.createElement('tr');
    sidebarTableRow.className = String(table) + "-row";
    
    var sidebarTableCell_name = sidebarTableRow.insertCell();
    var name = document.createElement('a');
    name.href = '../node/' + node.data.i;
    name.innerHTML = node.data.n;
    name.className = "sidebar-table-cell";
    sidebarTableCell_name.appendChild(name);
    
    var sidebarTableCell_type = sidebarTableRow.insertCell();
    var type = document.createElement("p");
    type.innerHTML = node.data.t;
    type.className = "sidebar-table-cell";
    sidebarTableCell_type.appendChild(type);
    
    var sidebarTableCell_location = sidebarTableRow.insertCell();
    if(node.data.l != null && node.data.api != "v2")
        sidebarTableCell_location.innerHTML = '<i class="fas fa-crosshairs fa-2x" onclick="locateNode(' + node.data.l[0] + ',' + node.data.l[1] + ')"></i>';
    else if(node.data.l != null && node.data.api == "v2") 
        sidebarTableCell_location.innerHTML = '<i class="fas fa-crosshairs fa-2x" onclick="locateAndShowNode(' + node.data.l[0] + ',' + node.data.l[1] + ',\'' + node.data.n + '\',\'' + node.data.t + '\',\'' + node.data.i + '\')"></i>';
    
    //Sort the nodes while adding them to the map sidebar table
    var rows = sidebarTable.getElementsByTagName("TR"), rowCell, i;
    if (rows.length == 1) {
        sidebarTable.appendChild(sidebarTableRow);
    }
    else {
        for (i = 1; i < (rows.length); i++) {
            rowCell = rows[i].getElementsByTagName("TD")[0];
            if (sidebarTableCell_name.firstChild.innerHTML.toLowerCase() < rowCell.firstChild.innerHTML.toLowerCase()){
                sidebarTable.insertBefore(sidebarTableRow, rows[i]);
                return;
            }
        }
        sidebarTable.appendChild(sidebarTableRow);
    }
}

//Search nodes in the map sidebar table
function sidebarSearch(input,table) {
    var input, filter, table, tr, td, i;
    input = document.getElementById(String(input));
    filter = input.value.toUpperCase();
    table = document.getElementById(String(table));
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            }
            else {
                tr[i].style.display = "none";
            }
        }
    }
}

//Pan to the selected node in the map sidebar
var map;

$(window).on('map:init', function(e) {
    map = e.originalEvent.detail.map;
});

function locateNode(lat,lon) {
    map.setView([lon, lat],20);
}

function locateAndShowNode(lat, lon, name, type, id) {
    var popup = L.popup()
        .setLatLng([lon, lat])
        .setContent('Name: <a href="../node/' + id + '">' + name + '</a><br>Type: ' + type)
        .openOn(map);
    map.setView([lon, lat],20);
}