import subprocess
import time
import optparse
import os.path
import traceback

from django.conf import settings
from django.core import management
from django.core import serializers
from django.core.management import base as management_base
from django.core.management import color as management_color
from django.db import connection, transaction

# TODO: Change all prints to self.stdout.write for Django 1.3

class Command(management_base.BaseCommand):
  """
  This class defines a command for manage.py which prepares and initializes the database.
  """

  args = "[dump_file]"
  help = "Prepare and initialize the database. If optional dump_file is specified it is used to populate the database."
  requires_model_validation = False
  option_list = management_base.BaseCommand.option_list + (
    optparse.make_option('--noinput', action='store_false', dest='interactive', default=True,
      help='Tells Django to NOT prompt the user for input of any kind.'),
  )
  
  def handle(self, *args, **options):
    """
    Prepares and initializes the database.
    """

    verbosity = int(options.get('verbosity', 1))
    interactive = options.get('interactive', True)
    show_traceback = options.get('traceback', False)

    def ensure_success(errcode):
      if errcode != 0:
        raise management_base.CommandError('Command failed to execute, aborting!')
    
    if len(args) > 1:
      raise management_base.CommandError('Too many arguments!')
    elif len(args) > 0 and not os.path.exists(args[0]):
      raise management_base.CommandError("Given dump file '%s' does not exist!" % args[0])
    
    # Determine the database backend
    db_backend = settings.DATABASES['default']['ENGINE']
    if db_backend.find('postgresql') != -1:
      db_backend = 'postgresql'
    elif db_backend.find('sqlite') != -1:
      db_backend = 'sqlite'
    elif db_backend.find('mysql') != -1:
      db_backend = 'mysql'
    
    # Close the connection before continuing since the setup script will
    # recreate databases
    connection.close()

	# TODO: manage.py script could be run somewhere else, with some other working directory
    if os.path.isfile('scripts/%s_init.sh' % db_backend):
      print "!!! NOTE: A setup script exists for your database. Be sure that it"
      print "!!! does what you want! You may have to edit the script and YOU"
      print "!!! MUST REVIEW IT! Otherwise the script may bork your installation."

      if interactive:
        print "Press CTRL + C to abort now."

        try:
          time.sleep(5)
        except KeyboardInterrupt:
          raise management_base.CommandError('Aborted by user.')

      if verbosity >= 1:
        print ">>> Executing database setup script 'scripts/%s_init.sh'..." % db_backend
      ensure_success(subprocess.call(["scripts/%s_init.sh" % db_backend, settings.DATABASES['default']['NAME']]))
    else:
      print "!!! NOTE: This command assumes that you have created and configured"
      print "!!! a proper database via settings.py! The database MUST be completely"
      print "!!! empty (no tables or sequences should be present). If this is not"
      print "!!! the case, this operation WILL FAIL!"
      
      if db_backend == 'postgresql':
        print "!!!"
        print "!!! You are using a PostgreSQL database. Be sure that you have"
        print "!!! installed the IP4R extension or schema sync WILL FAIL!"
        print "!!! "
        print "!!! More information: http://ip4r.projects.postgresql.org"
        print "!!!"
      
      if interactive:
        print "Press CTRL + C to abort now."

        try:
          time.sleep(5)
        except KeyboardInterrupt:
          raise management_base.CommandError('Aborted by user.')
    
    if len(args) > 0:
      options['interactive'] = False # We will populate with our data so no need for asking about admin user

    if verbosity >= 1:
      print ">>> Performing initial database sync..."
    management.call_command("syncdb", **options)
    
    if len(args) < 1:
      if verbosity >= 1:
        print ">>> Initialization completed."
      return

    if verbosity >= 1:
      print ">>> Performing data cleanup..."

    try:
      cursor = connection.cursor()
      cursor.execute("DELETE FROM auth_group_permissions")
      cursor.execute("DELETE FROM auth_group")
      cursor.execute("DELETE FROM auth_permission")
      cursor.execute("DELETE FROM auth_user")
      cursor.execute("DELETE FROM django_content_type")
      cursor.execute("DELETE FROM django_site")
      cursor.execute("DELETE FROM policy_trafficcontrolclass")
      transaction.commit_unless_managed()
    except:
      raise management_base.CommandError('Data cleanup operation failed, aborting!')
 
    if db_backend == 'mysql':
      connection.cursor().execute("SET FOREIGN_KEY_CHECKS = 0")
    elif db_backend == 'sqlite':
      connection.cursor().execute("PRAGMA foreign_keys = 0")
    transaction.commit_unless_managed()
    
    if verbosity >= 1:
      print ">>> Importing data from '%s'..." % args[0]

    transaction.enter_transaction_management()
    transaction.managed(True)

    models = set()
    
    try:
      count = 0
      for holder in serializers.deserialize('json', open(args[0], 'r')):
        models.add(holder.object.__class__)
        holder.save()
        count += 1
      if verbosity >= 1:
        print "Installed %d object(s)" % count
    except:
      transaction.rollback()
      transaction.leave_transaction_management()
    
      if show_traceback:
        traceback.print_exc()
      raise management_base.CommandError('Data import operation failed, aborting!')
    
    # Reset sequences
    for line in connection.ops.sequence_reset_sql(management_color.no_style(), models):
      cursor.execute(line)

    transaction.commit()
    transaction.leave_transaction_management()
    connection.close()

    # Additional syncdb for fixture overrides
    management.call_command("syncdb", **options)
    
    if verbosity >= 1:
      print ">>> Import completed."

