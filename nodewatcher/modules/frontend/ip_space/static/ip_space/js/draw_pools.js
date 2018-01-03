utilization
functutilization, y) {
    this.x = x;
    this.y = y;
}

Point.prototype = {
  rotate: function (n, x, y) {
      if (y === 0) {
          if (x === 1) {
              this.x = n-1 - this.x;
              this.y = n-1 - this.y;
          }

          this.x = [this.x, this.y = this.x][0];
      }
  }
};

/**
 * Maps a number to a x,y and returns the point
 * @param d The number to be mapped
 * @param n The maximum number of d (by default 2**32)
 * @returns {Point} A point to which d was mapped
 */
function d2xy(d, n=2**32) {
    var p = new Point(0, 0);
    var rx = 0;
    var ry = 0;
    var t=d;

    for (var s=1; s<n; s*=2) {
        rx = 1 & (t/2);
        ry = 1 & (t ^ rx);
        p.rotate(s, rx, ry);
        p.x += s * rx;
        p.y += s * ry;
        t /= 4;
    }
    return p;
}

/**
 * Maps a 2D point to a matching 1D number
 * @param p Point to be mapped
 * @param n Maximum value of 1D (by default 2**32)
 * @returns {number} The 1D mapped from a 2D point
 */
function xy2d(p, n=2**32){
        var rx;
        var ry;
        var d=0;
        for (var s=n/2; s>0; s/=2) {
            rx = (p.x & s) > 0;
            ry = (p.y & s) > 0;
            d += s * s * ((3 * rx) ^ ry);
            p.rotate(s, rx, ry);
        }
        return d;
}

/**
 * Maps a dot notation of IP to a number
 * @param ip Ip dotted notation
 * @returns {number} The number that matches the notation
 */
function ip2num(ip){
    ip = ip.split(".");
    return parseInt(ip[0])*256**3 + parseInt(ip[1])*256**2 + parseInt(ip[2])*256 + parseInt(ip[3]);
}

/**
 * Holds information about a pool
 * @param id Of a pool
 * @param ip Of network
 * @param prefix Of a pool
 * @param parent Parent object
 * @param description Description of a pool
 * @constructor
 */
function Pool(id, ip, prefix, parent, description){
    this.id = id;
    this.ip = ip;
    this.prefix = prefix;
    this.parent = parent;
    this.description = description;
    this.subnets = [];
    this.isTopLevel = false;
    this.utalization = 100;
    this.numberOfIps =  2 ** (32-prefix);
}

Pool.prototype = {
    /**
     * Adds a pool to the pools array of subnets
     * @param child
     */
    addSubnet: function (child) {
        this.subnets.push(child);
    },
    /**
     * Returns the percentage of pool utilization, if a pool has no subnets its utilization is 100 if not its calculated according to the utilization of subnets
     * @returns {number}
     */
    getUtilization(){
        if(this.subnets.length === 0){
            this.utalization = 100;
            console.log("this is leaf", this.ip+'/'+this.prefix, this.utalization, this.numberOfIps);
            return this.utalization;
        }
        this.utalization = 0;
        for(var i=0; i<this.subnets.length; i++){
            var item = this.subnets[i];
            this.utalization += (item.numberOfIps/this.numberOfIps) * item.getUtilization();
            console.log('current utalization', this.utalization);
        }
        console.log("this is not leaf", this.ip+'/'+this.prefix, this.utalization, this.numberOfIps);
        return this.utalization;
    }
};