#!/usr/bin/env python

# This script downloads daily database dump with real data, prepares the database for nodewatcher and injects data from dump

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'

# Settings
from django.conf import settings

import urllib
import tarfile

def report(count, size, all):
  if (count % 100 == 0):
    print "%.1f%% of %i bytes" % (100.0 * count * size / all, all)

print ">>> Retrieving dump data from the server..."
(filename, _) = urllib.urlretrieve("http://bindist.wlan-lj.net/data/dump.tar.bz2", reporthook=report)
try:
  file = tarfile.open(filename)
  print ">>> Uncompressing data..."
  print "data.json"
  file.extract("data.json")
  
  print "static files"
  static = file.getmembers()
  static.remove(file.getmember("data.json"))
  file.extractall(path=settings.MEDIA_ROOT, members=static)
  file.close()
finally:
  os.remove(filename)

import subprocess

print ">>> Preparing database and injecting data..."
if subprocess.call([sys.executable, '-u', 'prepare-database.py', 'data.json']) != 0:
  print "ERROR: Command failed to execute, aborting!"
  exit(1)
