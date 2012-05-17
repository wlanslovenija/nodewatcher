from nodewatcher.registry import registration
from nodewatcher.registry import forms as registry_forms
from nodewatcher.registry import cgm
from nodewatcher.registry.cgm import base as cgm_base

# Dependencies
import nodewatcher.core

# Load modules for all supported platforms
import nodewatcher.core.cgm.openwrt
import nodewatcher.core.cgm.ubnt
