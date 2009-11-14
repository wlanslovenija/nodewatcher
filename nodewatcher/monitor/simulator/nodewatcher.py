from lib import nodewatcher

# Load simulated output
SIMULATED_NODEWATCHER = open("simulator/data/nodewatcher.txt").read()

def parse_node_info(data):
  return nodewatcher.parse_node_info(data)

def fetch_node_info(node_ip):
  return parse_node_info(SIMULATED_NODEWATCHER)

def frequency_to_channel(frequency):
  return nodewatcher.frequency_to_channel(frequency)

def fetch_installed_packages(node_ip):
  return None

