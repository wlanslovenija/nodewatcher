from django import db
from django.core import exceptions as core_exceptions
from django.contrib.auth import models as auth_models
from django.core import urlresolvers
from django.db.migrations import exceptions as migrations_exceptions
from django.views import generic

from guardian import utils as guardian_utils

from nodewatcher.core.frontend import views

from . import forms


class SetupPage(views.CancelableFormMixin, generic.FormView):
    template_name = 'setup/setup.html'
    form_class = forms.AdminCreationForm
    success_url = urlresolvers.reverse_lazy('SetupComponent:setup')
    cancel_url = urlresolvers.reverse_lazy('SetupComponent:setup')

    def get_context_data(self, **kwargs):
        kwargs = super(SetupPage, self).get_context_data(**kwargs)

        kwargs.update({
            'pending_migrations': self.pending_migrations(),
            'create_admin': self.create_admin(),
        })

        return kwargs

    def pending_migrations(self):
        """
        Returns true if the set of migrations on disk don't match the
        migrations in the database.
        """

        from django.db.migrations.executor import MigrationExecutor
        try:
            executor = MigrationExecutor(db.connections[db.DEFAULT_DB_ALIAS])
        except core_exceptions.ImproperlyConfigured:
            # No databases are configured (or the dummy one).
            return False
        except migrations_exceptions.MigrationSchemaMissing:
            # Not checking migrations as it is not possible to access/create the django_migrations table.
            return False

        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            return True
        else:
            return False

    def create_admin(self):
        """
        Returns true if there are no users in the database.
        """

        return not auth_models.User.objects.exclude(pk=guardian_utils.get_anonymous_user().pk).exists()

    def form_valid(self, form):
        # Save/create the account.
        form.save()

        return super(SetupPage, self).form_valid(form)
