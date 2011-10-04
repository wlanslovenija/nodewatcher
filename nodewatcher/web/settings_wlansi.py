# -*- coding: utf-8 -*-
# Development Django settings for wlan slovenija nodewatcher installation

from settings import *

import os.path
wlansi_template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'wlansi', 'templates')

EMAIL_SUBJECT_PREFIX = '[wlan-si] '
EMAIL_EVENTS_SENDER = 'events@wlan-si.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@wlan-si.net'

NETWORK_NAME = 'wlan slovenija'
NETWORK_HOME = 'http://wlan-si.net'
NETWORK_CONTACT = 'open@wlan-si.net'
NETWORK_CONTACT_PAGE = 'http://wlan-si.net/contact/'
NETWORK_DESCRIPTION = 'odprto brezžično omrežje Slovenije'

# Where the map displaying all nodes is initially positioned
# Where the map is initially positioned when adding a new node is configured for each project in the database
GOOGLE_MAPS_DEFAULT_LAT = 46.17
GOOGLE_MAPS_DEFAULT_LONG = 14.96
GOOGLE_MAPS_DEFAULT_ZOOM = 8

TEMPLATE_DIRS = (
  wlansi_template_dir,
  default_template_dir,
)

IMAGES_BINDIST_URL = 'http://bindist.wlan-si.net/images/'

DOCUMENTATION_LINKS.update({
  'custom_node': 'http://dev.wlan-si.net/wiki/CustomNodes',
  'known_issues': 'http://dev.wlan-si.net/wiki/Nodewatcher/KnownIssues',
  'report_issue': 'http://dev.wlan-si.net/newticket',
  'solar': 'http://dev.wlan-si.net/wiki/Solar',
})
