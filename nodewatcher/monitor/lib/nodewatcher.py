from __future__ import with_statement
import urllib2
import socket
import threading
from Queue import Queue, Empty

class NodeWatcher(object):
  """
  Parser for nodewatcher feeds from nodes.
  """
  @staticmethod
  def fetch(nodeIp):
    """
    Fetches node information via HTTP.
    """
    socket.setdefaulttimeout(15)
    try:
      info = {}
      data = urllib2.urlopen('http://%s/cgi-bin/nodewatcher' % nodeIp).read(512 * 1024)
      for line in data.split('\n'):
        if not line:
          break

        if line[0] == ';':
          continue

        key, value = line.split(':', 1)
        value = value.strip()
        key = key.split('.')

        d = info
        for part in key[:-1]:
          d = d.setdefault(part, {})
        
        d[key[-1]] = value
    except:
      return None

    return info
  
  @staticmethod
  def frequency_to_channel(frequency):
    """
    Converts a given frequency to a channel number.
    """
    try:
      frequency = float(frequency)
      if frequency < 10:
        frequency *= 1000

      channels = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462, 2467, 2472, 2484]
      return channels.index(int(frequency)) + 1
    except:
      return 0

  @staticmethod
  def fetchInstalledPackages(nodeIp):
    """
    Fetches installed node packages.
    """
    socket.setdefaulttimeout(15)
    try:
      info = {}
      data = urllib2.urlopen('http://%s/cgi-bin/opkgwatcher' % nodeIp).read(512 * 1024)
      for line in data.split('\n'):
        if not line:
          break
        
        package, x, version, y = line.strip().split(' ')
        info[package] = version
    except:
      return None

    return info

  @staticmethod
  def spawnWorkers(ips, num_workers = 20):
    """
    Spawns workers to process stuff.

    @param ips: Node IPs
    @return: A dictionary with node information
    """
    work = Queue()
    for ip in ips:
      work.put(ip)

    done = {}
    doneLock = threading.Lock()
    workers = []

    for i in xrange(num_workers):
      workers.append(NodeWatcherWorker(work, done, doneLock))
    
    for worker in workers:
      worker.start()

    work.join()
    for worker in workers:
      worker.join()
    return done

class NodeWatcherWorker(threading.Thread):
  """
  A nodewatcher worker thread for parallel data fetch.
  """
  __workQueue = None
  __doneQueue = None
  __doneQueueLock = None
  
  def __init__(self, work, done, lock):
    """
    Class constructor.

    @param work: Work queue instance
    @param done: Done queue instance
    @param lock: Done queue lock
    """
    self.__workQueue = work
    self.__doneQueue = done
    self.__doneQueueLock = lock
    super(NodeWatcherWorker, self).__init__()
  
  def run(self):
    """
    Process items from the work queue.
    """
    if self.__workQueue is None or self.__doneQueue is None:
      return
    
    while True:
      try:
        ip = self.__workQueue.get(False)
        data = NodeWatcher.fetch(ip)

        with self.__doneQueueLock:
          self.__doneQueue[ip] = data

        self.__workQueue.task_done()
      except Empty:
        break

