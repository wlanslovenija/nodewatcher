import subprocess
import logging
from traceback import print_exc
from wlanlj.nodes.models import NodeType

class DotTopologyPlotter:
  """
  A topology plotter with Dot (Graphviz) output.
  """
  __output = None
  __edges = None

  def __init__(self):
    """
    Class constructor.
    """
    self.__output = ""
    self.__edges = {}

  def addNode(self, node):
    """
    Adds a new node.
    """
    if node.system_node:
      color = "#FFCB05"
    else:
      if node.node_type == NodeType.Server:
        color = "#E2F206"
      elif node.node_type == NodeType.Test:
        color = "#A7F206"
      elif node.node_type == NodeType.Unknown:
        color = "#F26006"
      else:
        color = "#BFCB05"
    
    if node.name:
      name = "%s\\n(%s)" % (node.name, node.ip)
    else:
      name = node.ip
    
    links = {}
    linksEtx = {}

    self.__output += '"%s" [label="%s",color="%s",style="filled"];\n' % (node.ip, name, color)
    for link in node.dst.all():
      if linksEtx.get(link.src.ip, 0) > link.etx:
        pass
      elif (node.ip, link.src.ip) in self.__edges or (link.src.ip, node.ip) in self.__edges:
        continue

      if link.etx < 1:
        continue
      elif link.etx >= 1 and link.etx <= 2:
        color = "green"
        weight = 20.0
      elif link.etx > 2 and link.etx <= 5:
        color = "blue"
        weight = 5.0
      else:
        weight = 0.7
        color = "red"

      links[link.src.ip] = '"%s" -- "%s" [label="%s",color="%s",weight="%s"];\n' % (node.ip, link.src.ip, link.etx, color, weight)
      linksEtx[link.src.ip] = link.etx
      self.__edges[(node.ip, link.src.ip)] = link.etx

    self.__output += "".join(links.values())

  def save(self, filename_graph, filename_dot):
    """
    Saves generated graph to a PNG file.

    @param filename_graph: The filename of resulting graph image
    @param filename_dot: The filename of resulting graph dot file
    """
    dot = open(filename_dot, 'w')
    dot.write("graph topology {\n%s}\n" % self.__output)
    dot.close()
    
    try:
      subprocess.check_call(
        [
          '/usr/bin/neato', '-Tpng',
          '-Gsize=10.0,1000.0', '-Gfontpath=/usr/share/fonts/corefonts',
          '-Nfontname=verdana', '-Nfontsize=12',
          '-Efontname=verdana', '-Efontsize=10', '-Elen=3', '-Earrowsize=1',
          '-o', filename_graph,
          filename_dot
        ]
      )
    except:
      logging.warning(print_exc())
