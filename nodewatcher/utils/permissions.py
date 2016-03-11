import itertools

from django import shortcuts
from django.db import models
from django.db.models import query
from django.contrib.contenttypes import models as contenttypes_models

from guardian import compat as guardian_compat, exceptions, utils as guardian_utils
