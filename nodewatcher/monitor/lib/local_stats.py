
from popen2 import popen2 as popen

def fetch_traffic_statistics():
  stats = {}
  rd, wr = popen("/sbin/iptables -v -n -x --list")
  while True:
    line = rd.readline()
    if not line:
      break
  
    if 'statistics:' not in line:
      continue

    line = line.strip().split()
    if len(line) != 11:
      continue

    try:
      int(line[0])
    except:
      continue

    bytes = int(line[1])
    comment = line[9]
    stats[comment] = bytes

  return stats

