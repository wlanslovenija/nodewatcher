var Point = window.Point = function(x, y, z) {
  if (x instanceof Array) {
    y = x[1];
    z = x[2];
    x = x[0];
  }

  this.x = Math.round(x) || 0;
  this.y = Math.round(y) || 0;
  this.z = Math.round(z) || 0;

  this.arr = [this.x, this.y, this.z];

  this.n = 4*this.z + 2*this.y + this.x;

  this.map = function(fn) {
    return new Point([x,y,z].map(fn));
  };

  this.mult = function(n) {
    return new Point(this.x*n, this.y*n, this.z*n);
  };

  this.add = function(n) {
    if (n instanceof Number) return new Point(this.x+n, this.y+n, this.z+n);
    return new Point(this.x + n.x, this.y + n.y, this.z + n.z);
  };

  this.mod = function(n) {
    return new Point(this.x % n, this.y % n, this.z % n);
  };

  this.rotate = function(regs, n) {
    if (regs.n == 0) {
      return new Point(this.z, this.x, this.y);
    } else if (regs.n == 1 || regs.n == 3) {
      return new Point(this.y, this.z, this.x);
    } else if (regs.n == 2 || regs.n == 6) {
      return new Point(n-this.x, n-this.y, this.z);
    } else if (regs.n == 5 || regs.n == 7) {
      return new Point(this.y, n-this.z, n-this.x);
    } else {  // regs.n == 4
      return new Point(n-this.z, this.x, n-this.y);
    }
  };

  this.unrotate = function(regs, n) {
    if (regs.n == 0) {
      return new Point(this.y, this.z, this.x);
    } else if (regs.n == 1 || regs.n == 3) {
      return new Point(this.z, this.x, this.y);
    } else if (regs.n == 2 || regs.n == 6) {
      return new Point(n-this.x, n-this.y, this.z);
    } else if (regs.n == 5 || regs.n == 7) {
      return new Point(n-this.z, this.x, n-this.y);
    } else {  // regs.n == 4
      return new Point(this.y, n-this.z, n-this.x);
    }
  };

  this.rotateLeft = function(n) {
    if (n%3 == 0) return this;
    if (n%3 == 1) return new Point(this.y, this.z, this.x);
    return new Point(this.z, this.x, this.y);
  };

  this.rotateRight = function(n) {
    if (n%3 == 0) return this;
    if (n%3 == 1) return new Point(this.z, this.x, this.y);
    return new Point(this.y, this.z, this.x);
  };

  this.shuffle = function(template) {
    if (!template) return this;
    return new Point(this[template[0]], this[template[1]], this[template[2]]);
  };

  this.pp = function() {
    return [this.x,this.y,this.z].join(',');
  };

  this.manhattanDistance = function(other) {
    return Math.abs(other.x - this.x) + Math.abs(other.y - this.y) + Math.abs(other.z - this.z);
  };
};
