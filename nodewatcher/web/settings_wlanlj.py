# coding=utf-8
# Development Django settings for wlan ljubjana network nodewatcher.

from settings import *

import os.path
wlanlj_template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'wlanlj', 'templates').replace('\\', '/')

EMAIL_SUBJECT_PREFIX = '[wlan-lj] '
EMAIL_EVENTS_SENDER = 'events@wlan-lj.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@wlan-lj.net'

NETWORK_NAME = 'wlan ljubljana'
NETWORK_HOME = 'http://wlan-lj.net'
NETWORK_CONTACT = 'open@wlan-lj.net'
NETWORK_CONTACT_PAGE = 'http://wlan-lj.net/contact'
NETWORK_DESCRIPTION = 'odprto brezžično omrežje Ljubljane'

SITE_ID = 2

# Where the map displaying all nodes is initially positioned
# Where the map is initially positioned when adding a new node is configured for each project in the database
GOOGLE_MAPS_DEFAULT_LAT = 46.05
GOOGLE_MAPS_DEFAULT_LONG = 14.507
GOOGLE_MAPS_DEFAULT_ZOOM = 13

TEMPLATE_DIRS = (
  wlanlj_template_dir,
  default_template_dir,
)

LOGIN_REDIRECT_URL = '/my/nodes'
LOGIN_URL = '/auth/login'
RESET_PASSWORD_URL = 'http://wlan-lj.net/reset_password'
PROFILE_CONFIGURATION_URL = 'http://wlan-lj.net/prefs'
REGISTER_USER_URL = 'http://wlan-lj.net/register'

IMAGES_BINDIST_URL = 'http://bindist.wlan-lj.net/images/'

DOCUMENTATION_LINKS.update({
  'custom_node'          : 'http://wlan-lj.net/wiki/Podrobnosti/PoMeri',
  'known_issues'         : 'http://wlan-lj.net/wiki/Podrobnosti/ZnaneTezave',
  'report_issue'         : 'http://wlan-lj.net/newticket',
  'diversity'            : 'http://wlan-lj.net/wiki/Diversity',
  'ip_address'           : 'http://wlan-lj.net/wiki/IPNaslov',
  'solar'                : 'http://wlan-lj.net/wiki/Podrobnosti/Solar',
  'antenna_type'         : 'http://wlan-lj.net/wiki/Antena',
  'antenna_polarization' : 'http://wlan-lj.net/wiki/Antena#Polarizacija',
  'vpn'                  : 'http://wlan-lj.net/wiki/VPN',
})
