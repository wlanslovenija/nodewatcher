#!/usr/bin/python
#
# wlan ljubljana Image Generator Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#
import os
import time

DESTINATION = "/var/www/nodes.wlan-lj.net/results"

for root, dirs, files in os.walk(DESTINATION):
  for file in files:
    file = os.path.join(root, file)
    if int(time.time() - os.path.getmtime(file)) > 86400 * 5:
      os.unlink(file)

