import urllib
import tarfile
import optparse
import os

from django.conf import settings
from django.core import management
from django.core.management import base as management_base

# TODO: Change all prints to self.stdout.write for Django 1.3

class Command(management_base.NoArgsCommand):
  """
  This class defines a command for manage.py which loads test
  (daily dump) data from nodes.wlan-si.net into the current database.
  """
  help = "Load test (daily dump) data from nodes.wlan-si.net into the current database."
  option_list = management_base.BaseCommand.option_list + (
    optparse.make_option('--noinput', action='store_false', dest='interactive', default=True,
      help='Tells Django to NOT prompt the user for input of any kind.'),
  )
  
  def handle_noargs(self, **options):
    """
    Loads test (daily dump) data from nodes.wlan-si.net into the current database.
    """
    verbosity = int(options.get('verbosity', 1))    

    def report(count, size, all):
      if verbosity < 1:
          return
      if (count % 100 == 0):
        print "%.1f%% of %i bytes" % (100.0 * count * size / all, all)
    
    if verbosity >= 1:
      print ">>> Retrieving test (daily dump) data from the server..."
    (filename, _) = urllib.urlretrieve("http://bindist.wlan-si.net/data/dump.tar.bz2", reporthook = report)

    try:
      file = tarfile.open(filename)
      if verbosity >= 1:
        print ">>> Uncompressing data..."
        print "data.json"
      file.extract("data.json")

      if verbosity >= 1:
        print "static files"
      static = file.getmembers()
      static.remove(file.getmember("data.json"))
      file.extractall(path = settings.MEDIA_ROOT, members = static)

      file.close()
    finally:
      os.remove(filename)
    
    # Call database initialization command
    management.call_command("preparedb", "data.json", **options)
