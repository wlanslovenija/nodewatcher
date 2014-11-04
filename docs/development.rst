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

This will recreate the `nodewatcher` database and thus erase ALL data from the database. If you wish to reinitialize the database at any later time, simply re-running the above command should work. Then, to populate the database with nodewatcher schema call `syncdb`::

    $ fig run web python manage.py syncdb

This will initialize the database schema.

Importing the JSON database dump from version 2
-----------------------------------------------

If you have a JSON data export from nodewatcher version 2 available and would like to migrate to version 3, the procedure is as follows (after you have already performed the database initialization above). Let us assume that the dump is stored in a file called `dump.json` (note that the dump file must be located inside the toplevel directory as commands are executed inside the container which only sees what is under the toplevel nodewatcher directory). The dump can be imported by running::

    $ fig run web python manage.py import_nw2 dump.json

Now the database is ready for use with nodewatcher 3.

Running management commands
---------------------------

Don't forget to run any management command via the container as otherwise the settings will be wrong. You can do it by prefixing commands with `fig run web` like this::

    $ fig run web python manage.py <command...>

Running a builder
-----------------

In order to develop firmware generator related functions, a firmware builder is provided with the development
installation. In order to use it, you have to configure it via the nodewatcher admin interface. First, you
have to create a default build channel and add a builder.

The following information should be used when adding a builder:

* **Host:** builder
*
    **Private key:**

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
