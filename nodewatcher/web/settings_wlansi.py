# coding=utf-8
# Development Django settings for wlan slovenija nodewatcher project.

from settings_wlanlj import *

import os.path
wlansi_template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'wlansi', 'templates').replace('\\', '/')

EMAIL_SUBJECT_PREFIX = '[wlan-si] '
EMAIL_EVENTS_SENDER = 'events@wlan-si.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@wlan-si.net'

NETWORK_NAME = 'wlan slovenija'
NETWORK_HOME = 'http://wlan-si.net'
NETWORK_CONTACT = 'open@wlan-si.net'
NETWORK_CONTACT_PAGE = 'http://wlan-lj.net/contact' # TODO
NETWORK_DESCRIPTION = 'odprto brezžično omrežje Slovenije'

SITE_ID = 3

# Where the map displaying all nodes is initially positioned
# Where the map is initially positioned when adding a new node is configured for each project in the database
GOOGLE_MAPS_DEFAULT_LAT = 46.17
GOOGLE_MAPS_DEFAULT_LONG = 14.96
GOOGLE_MAPS_DEFAULT_ZOOM = 8

TEMPLATE_DIRS = (
  wlansi_template_dir,
  default_template_dir,
)

RESET_PASSWORD_URL = 'http://wlan-lj.net/reset_password' # TODO
PROFILE_CONFIGURATION_URL = 'http://wlan-lj.net/prefs' # TODO
REGISTER_USER_URL = 'http://wlan-lj.net/register' # TODO

IMAGES_BINDIST_URL = 'http://bindist.wlan-lj.net/images/' # TODO
