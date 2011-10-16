#!/usr/bin/python
#
# nodewatcher Image Generator Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

# TODO: Move to manage.py command

import os
import time

DESTINATION = "/srv/www/bindist/images"

for root, dirs, files in os.walk(DESTINATION):
  for file in files:
    file = os.path.join(root, file)
    if int(time.time() - os.path.getmtime(file)) > 86400 * 5:
      os.unlink(file)

