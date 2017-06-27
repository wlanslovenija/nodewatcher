window.DrawCidr = class DrawCidr{
	constructor(svg, size, subnet){
		this.svg = svg;
		this.size = size;
		this.subnet = String(subnet);
		this.n_ips = Math.pow(2,32-parseInt(this.subnet.split("/")[1]));
		this.ips_side = Math.sqrt(this.n_ips);
		this.ips_pixel = this.ips_side/this.size;
		this.offset = this.ip2num(this.subnet.split("/")[0]);
		this.draw(subnet);
	}
	ip2num(ip){
                var d = ip.split('.');
                return ((((((+d[0])*256)+(+d[1]))*256)+(+d[2]))*256)+(+d[3]);
	}
	num2ip(num){
                var d = num%256;
                for (var i = 3; i > 0; i--)
                {
                    num = Math.floor(num/256);
                    d = num%256 + '.' + d;
                }
                return d;
	}
	subnetSize(subnet){
		var times = 32-parseInt(subnet.split("/")[1]);
		var subnet_ips = Math.pow(2, times);
		var shape_size = Math.sqrt(subnet_ips)/this.ips_pixel;
		return shape_size;
	}
	subnetXY(subnet){
		var start_num = this.ip2num(subnet.split("/")[0])-this.offset;
		var start_xy = d2xy(start_num);

		var x=start_xy.x/this.ips_pixel;
		var y=start_xy.y/this.ips_pixel;
		return [x,y];
	}
	HSVtoRGB(h, s, v) {
	    var r, g, b, i, f, p, q, t;
	    if (arguments.length === 1) {
		s = h.s, v = h.v, h = h.h;
	    }
	    i = Math.floor(h * 6);
	    f = h * 6 - i;
	    p = v * (1 - s);
	    q = v * (1 - f * s);
	    t = v * (1 - (1 - f) * s);
	    switch (i % 6) {
		case 0: r = v, g = t, b = p; break;
		case 1: r = q, g = v, b = p; break;
		case 2: r = p, g = v, b = t; break;
		case 3: r = p, g = q, b = v; break;
		case 4: r = t, g = p, b = v; break;
		case 5: r = v, g = p, b = q; break;
	    }
	    return {
		r: Math.round(r * 255),
		g: Math.round(g * 255),
		b: Math.round(b * 255)
	    };
	}
	componentToHex(c) {
	    var hex = c.toString(16);
	    return hex.length == 1 ? "0" + hex : hex;
	}

	rgbToHex(r, g, b) {
	    return "#" + this.componentToHex(r) + this.componentToHex(g) + this.componentToHex(b);
	}
	draw(subnet, description){
		var times = 32-parseInt(subnet.split("/")[1]);
		var subnet_ips = Math.pow(2, times);
		var shape_size = Math.sqrt(subnet_ips)/this.ips_pixel;

		var start_num = this.ip2num(subnet.split("/")[0])-this.offset;

		var start_xy = d2xy(start_num);

		var x=start_xy.x/this.ips_pixel;
		var y=start_xy.y/this.ips_pixel;

		this.svg.append("rect").attr("x", x).attr("y", y).attr("height", shape_size).attr("width", shape_size).style("fill", this.rgbToHex(times*8,times*8,times*8)).attr("id", subnet).attr("n", subnet_ips).attr("d", description);
	}
}
