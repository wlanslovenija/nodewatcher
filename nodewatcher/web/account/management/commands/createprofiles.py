from django.core import management
from django.core.management import base as management_base
from django.contrib.auth import models as auth_models
from django.db import transaction
from django.db.models import signals as models_signals

from web.account import utils

class Command(management_base.NoArgsCommand):
	"""
	This class defines an action for manage.py which populates database with user profiles for all users missing them.
	"""
	
	help = "Populate database with user profiles for all users missing them."

	def handle_noargs(self, **options):
		"""
		Populates database with user profiles for all users missing them.
		"""
		
		verbosity = int(options.get('verbosity', 1))
		model = utils.get_profile_model()
		for user in auth_models.User.objects.all():
			profile, created = model.objects.get_or_create(user=user)
			if verbosity == 2 and created:
				# TODO: Change to self.stdout.write
				print 'Created %s.' % profile
		transaction.commit_unless_managed()

def command_signal(sender, app, created_models, **kwargs):
	if utils.get_profile_model() in created_models:
		management.call_command('createprofiles', **kwargs)

models_signals.post_syncdb.connect(command_signal, sender=utils.get_profile_model().__module__)
