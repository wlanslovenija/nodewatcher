#!/usr/bin/python
#
# Wlan-Lj Image Generator Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

from beanstalk import serverconn
from beanstalk import job
import logging
import os

# Configure logger
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)-8s %(message)s',
                    datefmt = '%a, %d %b %Y %H:%M:%S',
                    filename = '/var/log/pnet.processor.log',
                    filemode = 'a')

c = serverconn.ServerConn("127.0.0.1", 11300)
c.use("generator")

try:
  while True:
    j = c.reserve()
    print j.data
    j.Release()
except:
  logging.warning("We are going down!")
