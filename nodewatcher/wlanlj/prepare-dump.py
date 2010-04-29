#!/usr/bin/env python

# This script is used to prepare daily database dump

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wlanlj.settings_production'

# Settings
from django.conf import settings

if len(sys.argv) != 2:
  print "Usage: %s output-file" % sys.argv[0]
  exit(1)

TMP_DIR = "/tmp/__wlanlj_dump_package"

os.mkdir(TMP_DIR)
os.system("python manage.py dumpdata --settings=wlanlj.settings_production > /tmp/__wlanlj_dump.json")
os.system("./sanitize-dump.py json /tmp/__wlanlj_dump.json %s/data.json" % TMP_DIR)
os.system("cp -R %s %s" % (settings.GRAPH_DIR, TMP_DIR))
os.system(r"find %s -name .svn -type d -exec rm -rf '{}' \; 2>/dev/null" % TMP_DIR)
os.unlink("/tmp/__wlanlj_dump.json")
os.chdir(TMP_DIR)
os.system("tar cfj %s *" % sys.argv[1])
os.system("rm -rf %s" % TMP_DIR)

