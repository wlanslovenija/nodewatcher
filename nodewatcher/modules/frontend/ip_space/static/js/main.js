$(document).ready(function() {
  var svgContainer = d3.select('#ipspace');
  var size = svgContainer.node().getBoundingClientRect().width;
  svgContainer.style('height', size + 'px');
  var main_subnet = '10.0.0.0/8';

  var cidr = new DrawCidr(svgContainer, size, main_subnet);
  cidr.load();

  $('#cidr').click(function() {
    var scale = size / cidr.subnetSize(this.value);
    var start = cidr.subnetXY(this.value);
    svgContainer.selectAll('rect').attr('transform', 'translate(' + start[0] * -1 * scale + ',' + start[1] * -1 * scale + ') scale(' + scale + ')');
  });
});