from frontend.registry import registration
from frontend.registry import forms as registry_forms
from frontend.registry import cgm
from frontend.registry.cgm import base as cgm_base

# Dependencies
import frontend.core

# Load modules for all supported platforms
import frontend.core.cgm.openwrt
import frontend.core.cgm.ubnt
