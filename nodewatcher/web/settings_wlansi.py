# -*- coding: utf-8 -*-
#
# Development Django settings for wlan slovenija nodewatcher

from settings import *

import os.path
wlansi_dir = os.path.join(settings_dir, '..', '..', 'wlansi')
wlansi_template_dir = os.path.join(wlansi_dir, 'templates')

EMAIL_SUBJECT_PREFIX = '[wlan-si] '
EMAIL_EVENTS_SENDER = 'events@wlan-si.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@wlan-si.net'

NETWORK_NAME = 'wlan slovenija'
NETWORK_HOME = 'http://wlan-si.net'
NETWORK_CONTACT = 'open@wlan-si.net'
NETWORK_CONTACT_PAGE = 'http://wlan-si.net/contact/'
NETWORK_DESCRIPTION = 'open wireless network of Slovenia'
NETWORK_FAVICON_URL = MEDIA_URL + 'wlansi/images/favicon.ico'
NETWORK_LOGO_URL = MEDIA_URL + 'wlansi/images/logo.png'

TEMPLATE_DIRS = (
  wlansi_template_dir,
) + TEMPLATE_DIRS

IMAGES_BINDIST_URL = 'http://bindist.wlan-si.net/images/'

DOCUMENTATION_LINKS.update({
  'custom_node': 'http://dev.wlan-si.net/wiki/CustomNodes',
  'known_issues': 'http://dev.wlan-si.net/wiki/Nodewatcher/KnownIssues',
  'report_issue': 'http://dev.wlan-si.net/newticket',
  'solar': 'http://dev.wlan-si.net/wiki/Solar',
})
