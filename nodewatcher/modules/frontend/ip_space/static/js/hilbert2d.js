var Hilbert2d = window.Hilbert2d = function(options, axisOrderOpt) {
  options = options || {};
  if (typeof options == 'number') {
    this.size = options;
    this.anchorAxisOrder = axisOrderOpt || 'xy';
  } else if (typeof options == 'string') {
    this.anchorAxisOrder = options;
  } else {
    // should be empty if we're prioritizing bottom level.
    this.size = options.top;
    this.anchorAxisOrder = options.axisOrder || 'xy';
  }

  if (!(this.anchorAxisOrder in {xy:1,yx:1})) {
    throw new Error("Invalid axis order: " + anchorAxisOrder);
  }

  if (this.size) {
    this.log2size = 0;
    var pow2 = 1;
    for (; pow2 < this.size; pow2 *= 2, this.log2size++) {}
    if (pow2 != this.size) {
      throw new Error("Invalid size: " + this.size + ". Must be a power of 2.");
    }
    this.log2parity = (this.log2size % 2);
  }

  function invert(point) {
    return {
      x: point.y,
      y: point.x
    };
  };

  function maybeRotate(point, iter) {
    if (this.size) {
      if (this.anchorAxisOrder == 'xy') {
        if (iter ^ this.log2parity) {
          return invert(point);
        }
      }
      if (this.anchorAxisOrder == 'yx') {
        if (!(iter ^ this.log2parity)) {
          return invert(point);
        }
      }
    } else {
      if (this.anchorAxisOrder == 'xy') {
        if (iter == 0) {
          return invert(point);
        }
      } else {
        if (iter == 1) {
          return invert(point);
        }
      }
    }
    return point;
  };

  this.d2xy = this.xy = function (d) {
    d = Math.floor(d);
    var curPos = {
      x: 0,
      y: 0
    };
    var s = 1;
    var iter = 0;
    var size = this.size || 0;
    while (d > 0 || s < size) {
      var ry = 1 & (d / 2);
      var rx = 1 & (ry ^ d);

      // Rotate, if need be
      if (rx == 0) {
        if (ry == 1) {
          curPos = {
            x: s - 1 - curPos.x,
            y: s - 1 - curPos.y
          };
        }
        curPos = invert(curPos);
      }

      curPos = {
        x: curPos.x + s * rx,
        y: curPos.y + s * ry
      };

      s *= 2;
      d = Math.floor(d / 4);
      iter = (iter + 1) % 2;
    }
    return maybeRotate(curPos, iter);
  };

  var horseshoe2d = [0, 1, 3, 2];

  this.xy2d = this.d = function (x, y) {
    var curPos = {
      x: Math.floor(x),
      y: Math.floor(y)
    };
    var s = 1;
    var level = 1;
    var max = Math.max(curPos.x, curPos.y);
    for (; 2 * s <= max; s *= 2) {
      level = (level + 1) % 2;
    }
    curPos = maybeRotate(curPos, level);

    var d = 0;
    while (s > 0) {
      var rx = curPos.x & s && 1;
      var ry = curPos.y & s && 1;
      d *= 4;
      d += horseshoe2d[2 * ry + rx];
      if (rx == 0) {
        if (ry == 1) {
          curPos = {
            x: s - 1 - curPos.x,
            y: s - 1 - curPos.y
          }
        }
        curPos = invert(curPos);
      }
      curPos = {
        x: curPos.x % s,
        y: curPos.y % s
      };
      s = Math.floor(s / 2);
    }
    return d;
  };
};
var h2 = new Hilbert2d();
window.d2xy = h2.d2xy;
window.xy = h2.xy;
window.xy2d = h2.xy2d;
window.d2 = h2.d;
