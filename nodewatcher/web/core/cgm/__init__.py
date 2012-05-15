from web.registry import registration
from web.registry import forms as registry_forms
from web.registry import cgm
from web.registry.cgm import base as cgm_base

# Dependencies
import web.core

# Load modules for all supported platforms
import web.core.cgm.openwrt
import web.core.cgm.ubnt
