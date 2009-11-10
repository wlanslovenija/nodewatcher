import subprocess

def fetch_traffic_statistics():
  """
  Fetches local traffic statistics from iptables.
  """
  stats = {}
  process = subprocess.Popen(
    ['/sbin/iptables', '-v', '-n', '-x', '--list'],
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  
  while True:
    line = process.stdout.readline()
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

