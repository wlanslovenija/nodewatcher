$(document).ready(function () {
    //Create d3 object on #ipspace
    var svgContainer = d3.select('#ipspace');

    //Get bootstrap width and match it in height
    var size = svgContainer.node().getBoundingClientRect().width;
    svgContainer.style('height', size + 'px');

    //Init vars
    var max_x = 0;
    var max_y = 0;
    var min_x = 65536;
    var min_y = 65536;
    var last_size = 0;

    //For each top level node check what is the min and the max and save it
    $('#topnodes > li').each(function (data) {
        var start_xy = d2xy(Support.ip2num(Support.cidrToRange($(this).attr('cidr'))[0]));
        var size = Support.subnetSize($(this).attr('cidr'));
        console.log(start_xy, size);

    });

    //Convert min and max cords to number
    var start_num = xy2d(min_x, min_y);
    var stop_num = xy2d(max_x + last_size, max_y + last_size);

    //Calculate the smallest number to fit both min and max
    var ips_needed = stop_num - start_num;
    var mask = 0;
    while (ips_needed > Math.pow(2, mask)) {
        mask++;
    }
    mask = 32 - mask;

    //Convert starting number to ip
    var start_ip = Support.num2ip(start_num);
    var min_subnet = start_ip + '/' + mask;

    //Add zoom to fit to list of subnets
    $('#topnodes').prepend('<li id="cidr" cidr="' + min_subnet + '"><a>' + min_subnet + ' (Zoom to fit)</a></li>');
    var api_url = $('#api_url').data('url');

    //Init drawing object and load all the ip pools
    var cidr = new DrawCidr(svgContainer, size, min_subnet, api_url);
    cidr.load();
});