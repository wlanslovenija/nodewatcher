Setting up the development environment
======================================

In order to make nodewatcher development as simple as possible, a Docker_ development environment can be built from the provided Dockerfile. To help with preparing the environment and running common tasks, fig_ configuration is also provided. This section describes how to use both to work on nodewatcher. It is assumed that Docker and fig are already installed, so in order to install them, please follow the guides on their respective pages.

.. _Docker: https://docker.io
.. _fig: https://orchardup.github.io/fig

Running the development server
------------------------------

To run the development server simply execute the following command in the top-level nodewatcher directory::

    $ fig up

The first time this command is executed, a new Docker image for nodewatcher development version will be built, which might take some time. On subsequent runs, the development server will be started immediately.

.. note:: Default container configuration stores the database under `/tmp/nodewatcher-db`, so it will be removed on host machine restarts. You may change this location by editing `fig.yml`.

Initializing the database
-------------------------

.. note:: This and all further sections assume that the development environment has been started via `fig up` and is running (in the background or in another terminal). If the environment is not running, some of the following commands will fail.

In order to prepare the database, after running the development server execute::

    $ fig run web scripts/docker-init-database

This will recreate the `nodewatcher` database and thus erase ALL data from the database. If you wish to reinitialize the database at any later time, simply re-running the above command should work.

Importing a database dump from version 2
----------------------------------------

If you have an SQL dump from nodewatcher version 2 available and would like to migrate to version 3, the procedure is as follows. Lets assume that the dump is stored in a filed called `dump.sql` (note that the dump file must be located inside the toplevel directory as commands are executed inside the container which only sees what is under the toplevel nodewatcher directory). First the dump must be preprocessed before it can be imported::

    $ ./scripts/convert-wlansi-v2-dump dump.sql

After the script completes, the dump must be imported into the development database. This can be done by running::

    $ fig run web scripts/docker-import-dump dump.sql

After the dump has been imported, migrations have to be run::

    $ fig run web scripts/migrate-v2-to-v3

Now the database is ready for use with nodewatcher 3.

Running management commands
---------------------------

Don't forget to run any management command via the container as otherwise the settings will be wrong. You can do it by prefixing commands with `fig run web` like this::

    $ fig run web python manage.py <command...>
