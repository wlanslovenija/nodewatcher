from lib import nodewatcher
import os

# Load simulated output
SIMULATED_NODEWATCHER_BASE = "simulator/data/nodes"

def parse_node_info(data):
  return nodewatcher.parse_node_info(data)

def fetch_node_info(node_ip):
  try:
    return parse_node_info(open(os.path.join(SIMULATED_NODEWATCHER_BASE, "%s.txt" % node_ip)).read())
  except:
    return None

def frequency_to_channel(frequency):
  return nodewatcher.frequency_to_channel(frequency)

def fetch_installed_packages(node_ip):
  return None

