function cidrToRange(cidr) {
    var range = [2];
    cidr = cidr.split('/');
    var start = ip2num(cidr[0]);
    range[0] = num2ip(start);
    range[1] = num2ip(Math.pow(2, 32 - cidr[1]) + start - 1);
    return range;
}

function ip2num(ip) {
    var d = String(ip).split('.');
    return ((((((+d[0]) * 256) + (+d[1])) * 256) + (+d[2])) * 256) + (+d[3]);
}

function num2ip(num) {
    var d = num % 256;
    for (var i = 3; i > 0; i--) {
        num = Math.floor(num / 256);
        d = num % 256 + '.' + d;
    }
    return d;
}

function subnetSize(subnet) {
    var subnet_str = String(subnet);
    var times = 32 - parseInt(subnet_str.split("/")[1]);
    var subnet_ips = Math.pow(2, times);
    var ips_side = Math.sqrt(subnet_ips);
    var ips_pixel = ips_side / (65536 * 1.0);
    var shape_size = Math.sqrt(subnet_ips) / ips_pixel;
    return shape_size;
}

$(document).ready(function () {
    var svgContainer = d3.select('#ipspace');
    var size = svgContainer.node().getBoundingClientRect().width;
    svgContainer.style('height', size + 'px');

    var max_x = 0;
    var max_y = 0;
    var min_x = 65536;
    var min_y = 65536;
    var last_size = 0;

    $('#topnodes > li').each(function (data) {
        if (d2xy(ip2num(cidrToRange($(this).attr('cidr'))[0])).x > max_x) {
            max_x = d2xy(ip2num(cidrToRange($(this).attr('cidr'))[0])).x;
            last_size = subnetSize($(this).attr('cidr'));
        }
        if (d2xy(ip2num(cidrToRange($(this).attr('cidr'))[0])).y > max_y) {
            max_y = d2xy(ip2num(cidrToRange($(this).attr('cidr'))[0])).y;
            last_size = subnetSize($(this).attr('cidr'));
        }
        if (d2xy(ip2num(cidrToRange($(this).attr('cidr'))[1])).y > max_y) {
            max_y = d2xy(ip2num(cidrToRange($(this).attr('cidr'))[1])).y > max_y;
            last_size = subnetSize($(this).attr('cidr'));
        }
        if (d2xy(ip2num(cidrToRange($(this).attr('cidr'))[1])).x > max_x) {
            max_x = d2xy(ip2num(cidrToRange($(this).attr('cidr'))[1])).x;
            last_size = subnetSize($(this).attr('cidr'));
        }
    });

    var start_num = xy2d(min_x, min_y);
    var stop_num = xy2d(max_x + last_size, max_y + last_size);

    var ips_needed = stop_num - start_num;
    var mask = 0;
    while (ips_needed > Math.pow(2, mask)) {
        mask++;
    }
    mask = 32 - mask;

    var start_ip = num2ip(start_num);
    var min_subnet = start_ip + '/' + mask;
    $('#topnodes').prepend('<li id="cidr" cidr="' + min_subnet + '"><a>' + min_subnet + ' (Zoom to fit)</a></li>');
    var api_url = $('#api_url').data('url');
    var cidr = new DrawCidr(svgContainer, size, min_subnet, api_url);
    cidr.load();
});