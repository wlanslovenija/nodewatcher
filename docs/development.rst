Setting up the development environment
======================================

In order to make nodewatcher development as simple as possible, a Docker_ development environment can be built from the provided Dockerfile. To help with preparing the environment and running common tasks, fig_ configuration is also provided. This section describes how to use both to work on nodewatcher. It is assumed that Docker and fig are already installed, so in order to install them, please follow the guides on the respective pages.

.. _Docker: https://docker.io
.. _fig: https://orchardup.github.io/fig

Running the development server
------------------------------

To run the development server simply execute the following command in the top-level nodewatcher directory::

    $ fig up

The first time this command is executed, a new Docker image for nodewatcher development version will be built, which might take some time. On subsequent runs, the development server will be started immediately.

Running management commands
---------------------------

TODO
