Setting up the development environment
======================================

In order to make nodewatcher development as simple as possible, a Docker_ development environment can be built from the provided Dockerfile. To help with preparing the environment and running common tasks, `Docker Compose`_ configuration is also provided. This section describes how to use both to work on nodewatcher. It is assumed that Docker and `Docker Compose` are already installed, so in order to install them, please follow the guides on their respective pages.

.. _Docker: https://www.docker.com
.. _Docker Compose: https://docs.docker.com/compose/

Running the development instance
--------------------------------

In order to ensure that you have the latest versions of all dependent Docker images, you have to first run the following command in the top-level nodewatcher directory::

    $ docker-compose pull

Then, to build the development instance, run::

    $ docker-compose build

You should re-run these two commands when performing ``git pull`` if you think that the build dependencies or development environment configuration might have changed to ensure that your Docker images are synced. Finally, to run the development server simply execute the following command::

    $ docker-compose up

.. note:: Default container configuration stores the database under ``/tmp/nodewatcher-db``, so it will be removed on host machine restarts. You may change this location by editing ``docker-compose.yml``.

The following containers will be created and started when you run the above commands:

* ``db`` contains the PostgreSQL 9.3 database server with installed extension PostGIS 2.1.
* ``tokumx`` contains the TokuMX database server (an improved version of MongoDB).
* ``redis`` contains the Redis server.
* ``builder{ar71xx,lantiq}`` contain firmware builders that you can use for development (see :ref:`development-run-builder`).
* ``generator`` contains the Celery workers for the firmware image generator. These workers connect to the ``builder`` via SSH in order to build firmware images.
* ``monitorq`` contains the Celery workers for handling monitoring push requests.
* ``web`` contains the nodewatcher frontend (Django development server), running on port ``8000`` by default.

.. note::
    The development instance uses TokuMX (an improved version of MongoDB) as a database server for storing datapoints. TokuMX requires that the use of HugePages be disabled in the kernel, otherwise the server will refuse to start. This is why the container is configured as privileged in ``docker-compose.yml``, so that it can disable this by default. In case you need to disable HugePages manually, you should execute the following on the host::

        $ echo never > /sys/kernel/mm/transparent_hugepage/enabled

Initializing the database
-------------------------

.. note:: This and all further sections assume that the development environment has been started via ``docker-compose up`` and is running (in the background or in another terminal). If the environment is not running, some of the following commands will fail.

In order to prepare the database, after running the development server execute::

    $ docker-compose run web scripts/docker-init-database

This will recreate the ``nodewatcher`` database and thus erase ALL data from the database. If you wish to reinitialize the database at any later time, simply re-running the above command should work. Then, to populate the database with nodewatcher schema call ``migrate``::

    $ docker-compose run web python manage.py migrate

This will initialize the database schema.

.. note::
    When running any Django management command, do not forget to run it via the container as otherwise the settings
    will be wrong. You can do it by prefixing commands with ``docker-compose run web`` like this::

        $ docker-compose run web python manage.py <command...>

Compile stylesheets
-------------------

For default nodewatcher stylesheets we are using `Compass`_, which means that SCSS files have to be
compiled into CSS files before CSS files can be served to users. Compass is built on top of `Sass`_,
which is an an extension of CSS3 and adds nested rules, variables, mixins, selector inheritance, and more.
Sass generates well formatted CSS and makes our stylesheets easier to organize and maintain.
It also makes stylesheets easier to extend and reuse so it is easier to build on default nodewatcher
stylesheets and add small changes you might want to add for your installation.

To compile SCSS files into CSS files run::

    $ docker-compose run web python manage.py collectstatic -l

.. _Compass: http://compass-style.org/
.. _Sass: http://sass-lang.com/

Initial setup
-------------

From scratch
............

If you are installing the nodewatcher from scratch, you should probably now create a Django admin account.
You can do this by opening nodewatcher initial setup page at `http://localhost:8000/setup/`_, and
follow instructions there.

Afterwards, you can login with this account into the nodewatcher at http://localhost:8000/account/login/
or into the nodewatcher's admin interface at http://localhost:8000/admin/.

.. note::
    Depending on your Docker installation the web interface might not be available at ``localhost``
    but at some other address.

.. _http://localhost:8000/setup/: http://localhost:8000/setup/

From nodewatcher v2 dump
........................

If you have a JSON data export from nodewatcher version 2 available and would like to migrate to version 3,
the procedure is as follows (after you have already performed the database initialization above). Let us assume
that the dump is stored in a file called ``dump.json`` (note that the dump file must be located inside the top-level
directory as commands are executed inside the container which only sees what is under the toplevel nodewatcher
directory). The dump can be imported by running::

    $ docker-compose run web python manage.py import_nw2 dump.json

Now the database is ready for use with nodewatcher 3.

.. _development-run-builder:

Running a builder
-----------------

In order to develop firmware generator related functions, a firmware builder is provided with the development
installation. In order to use it, you have to configure it via the nodewatcher admin interface. First, you
have to create a default build channel and add a builder (or multiple builders if you want support for multiple architectures).

The following information should be used when adding a builder:

* **Host:**
    * builderar71xx
    * builderlantiq
* **Private key:**

    ::

        -----BEGIN RSA PRIVATE KEY-----
        MIIEpQIBAAKCAQEAoaOhSCNIim6VPg6SakvQEbZ+I2l2QLnPOkJGgnNBQimmkIdk
        KH4M07ImzyApLMl38USTOa5RMMAH+kcHhq7ajOPaWRr5oUtH4aAqJhjQtqgDQ5AD
        5bwIbNiT6f4xXh+8A1VEK/g9TaHOHWjm3XQu660bTWtHIfZwH2AkyXMUhaevVXFI
        o/SF+zuutMOAi9ny/Mmvz+N39iGVanBXnz3mOf08nXhPBjGUKOS/u0SjEfa4WeCW
        PQkG0IApIZfSENjnOOnUw6FLcXueehFqd4KgUb3eAl3DJQ0t43dTr1uRxySyIEOu
        rrkvAvSOVW83KcaVfqnzsRHllxkYXdFfR+v9pwIDAQABAoIBAQCasF0GC3Y9vQyo
        wgtPHNS4TtyyiRg5Y1k1mP2flCts5S1ZfajVs6QU6JaJfG7LRNe7lvQKrI9Yxz4b
        P+Ss+SOA2AI7ajxiJwhYng4YPYFofKv6+ZUxQ90QRchwk+qs+FPXIL/IEJ6ib+ow
        bRcb8jeBJj5Nvg/qKc0tybYK8E5AhS7FF6JfCtRff6IWch0vFDHoml7J4VS1dFYt
        N/HcXPMM+Semf50LzyOvF1Yc/BWFpzmKG14qsGgJ/GBEw5UfI/oJKVBG95T+Lvk3
        1zeDQGMYiOSBbaem/u5rR3erkRiGroYN6qbAWSKd9ZNtXyyRlyBSO/iJkNYsFMeq
        hnaw8DfZAoGBANYFtHjvl1LtTVjpS/oa5b1ik/MkcE/qiAdve8zzYrlQclDkhFeT
        Eqq0geSQrWJ28+xfxVndRjO1DykJ8ye45myQTXqQS592qFs21WMOJxWw+phT+CQ1
        VMV0mlOpT/n1FisoTFQ4cv66zT3IY8ZH6PtNt3L0U4UzDbTJi+JBoXtlAoGBAMFX
        tib24wIObtpoqRD0+ZOtnPg9t4wE6vteFkGVSxXy7w32DxuQFW6lzJI9z4yVU37I
        VaTQ+hFECUmXRkGWgLziNMcIpQ6Q5KD0ZhfurrzCfF5tYQIZPbbpN3qy6xs/frnb
        gG0hts+aNQga6Oj3f/fxNuacNPioq5am+BtOnXIbAoGAD9usW6mlFMfwiz3+GzIT
        A81iGQoCKGnAWoywJ6eBESoczlGgXLzRDUUCuuTddAZMXJ9cCCSVJw+rZ+cM1Uym
        BjVLCGHYuKAaKWgOt6A81Saf6tmN8WDiPx88sCZDfsniMqBxx2vHWYiN3J4UhoSd
        hsFjbmkcJyp5QYQNkV47kOECgYEAnou8tWsTcKZBRR06NsuMtgtSg0ao80s9HnBj
        M9inQBJ88ifq76FR0fBoNyw0vIXfeEHz6TntNqdiLlS8qiAu5bVhri1qnO04bry7
        07hI1kVuE0kCmeP09b99XULHBQsmcmaLg/J3pPpBrqnSgOgkqj/F04oY7ifyvZGi
        N1JaTi0CgYEAsH1m5atSGjScUMiVTiWjnYB2E00cBB6a84UfS359+LvkJdDHRptt
        IjAnJaI31jpR2GSIQ9ck5SVNRKn8TO7hGMncSq6/CCJTwdAI9pzED4typVs341Wo
        BZ9HO5E5TUQTXTKkKR4kPT2wyfsjCBEJl76RIt7WyJnEbj1fIcn+OZo=
        -----END RSA PRIVATE KEY-----

    .. warning::

        This public/private key pair should only be used for development. For production deployments
        you should generate new key pairs and configure them appropriately (the public key can be
        configured by setting the ``BUILDER_PUBLIC_KEY`` environmental variable on the builder Docker
        container).

        In order to generate a new RSA key pair, you may use::

            $ ssh-keygen -f builder.key -C "builder@host"

        This will generate a ``builder.key`` (private key) and ``builder.key.pub`` (public key).

Running the monitoring system
-----------------------------

In order to enable data collection from nodes, the monitoring system needs to be running. It is important that the nodewatcher instance is able to connect to the nodes directly by their IP addresses. This can usually be achieved by establishing a VPN tunnel to some server that is connected to the mesh network.

Then, there are two configuration options that need to be set in ``settings.py``:

* ``OLSRD_MONITOR_HOST`` should point to an IP address where an ``olsrd`` instance is responding to HTTP requests about the routing state using the ``txtinfo`` plugin. In the default configuration, this will be used by the ``modules.routing.olsr`` module to enumerate visible nodes and obtain topology information.
* ``MEASUREMENT_SOURCE_NODE`` should be set to an UUID of a node that is performing the RTT measurements (this means that such a node must first be created using nodewatcher). This option is planned to be removed from ``settings.py`` and moved into the administration interface.

After the above settings are configured, one may run the monitoring system by issuing::

    $ docker-compose run web python manage.py monitord

There are some additional options which might be useful during development:

* ``--run=<run>`` will only execute one run instead of all runs configured using ``MONITOR_RUNS`` setting.
* ``--cycles=<cycles>`` will only perform a fixed amount of cycles before terminating. By default, the monitor process will run indefinitely.
* ``--process-only-node=<node-uuid>`` may be used to only perform monitoring processing on a single node, identified by its UUID.

.. note:: The monitoring system may use a lot of CPU and memory resources when there are a lot of nodes to process.
