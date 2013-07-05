# We override runserver command with basic runserver command which does not
# dynamically serve static files so that post-processing SCSS files work
# Static files have to be collected manually before running this command
# TODO: Check if there is some way to make it work with staticfiles' runserver
# TODO: Check if there is a way that it would automatically regenerate files on any file change during development
from django.core.management.commands.runserver import Command
