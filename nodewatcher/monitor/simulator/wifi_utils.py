from lib import wifi_utils

# Load simulated output
SIMULATED_ROUTER = open("simulator/data/olsr.txt").read()
SIMULATED_FPING = open("simulator/data/fping.txt").read()

def parse_tables(data):
  return wifi_utils.parse_tables(data)

def get_tables(olsr_ip = None):
  return parse_tables(SIMULATED_ROUTER)

def parse_fping(data):
  return wifi_utils.parse_fping(data)

def ping_hosts(count, hosts):
  return parse_fping(SIMULATED_FPING)

