from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import urllib
import tarfile
import os

class Command(BaseCommand):
  """
  Load test data command.
  """
  args = ""
  help = "Loads test data from nodes.wlan-lj.net into the current database"
  
  def handle(self, *args, **kwargs):
    """
    Command handler.
    """
    def report(count, size, all):
      if (count % 100 == 0):
        print "%.1f%% of %i bytes" % (100.0 * count * size / all, all)
    
    print ">>> Retrieving dump data from the server..."
    (filename, _) = urllib.urlretrieve("http://bindist.wlan-lj.net/data/dump.tar.bz2", reporthook = report)
    try:
      file = tarfile.open(filename)
      print ">>> Uncompressing data..."
      print "data.json"
      file.extract("data.json")
      
      print "static files"
      static = file.getmembers()
      static.remove(file.getmember("data.json"))
      file.extractall(path = settings.MEDIA_ROOT, members = static)
      file.close()
    finally:
      os.remove(filename)
    
    # Call database initialization command
    call_command("preparedb", "data.json")

