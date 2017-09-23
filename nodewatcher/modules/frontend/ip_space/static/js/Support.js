//Init support object
window.Support = {};

//cidrToRange converts cidr to starting number and ending number of subnet
window.Support.cidrToRange = function cidrToRange(cidr) {
    var range = [2];
    cidr = cidr.split('/');
    var start = Support.ip2num(cidr[0]);
    range[0] = Support.num2ip(start);
    range[1] = Support.num2ip(Math.pow(2, 32 - cidr[1]) + start - 1);
    return range;
};

//ip2num converts ip to a number
window.Support.ip2num = function ip2num(ip) {
    var d = String(ip).split('.');
    return ((((((+d[0]) * 256) + (+d[1])) * 256) + (+d[2])) * 256) + (+d[3]);
};

//num2ip converts number to dot notation
window.Support.num2ip = function num2ip(num) {
    var d = num % 256;
    for (var i = 3; i > 0; i--) {
        num = Math.floor(num / 256);
        d = num % 256 + '.' + d;
    }
    return d;
};

//returns the displayed size of a subnet prefix
window.Support.subnetSize = function subnetSize(subnet) {
    var subnet_str = String(subnet);
    var times = 32 - parseInt(subnet_str.split("/")[1]);
    console.log(times);
    var subnet_ips = Math.pow(2, times);
    return Math.sqrt(subnet_ips);
};