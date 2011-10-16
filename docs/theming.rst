Theming
=======

It is possible to configure distributed *nodewatcher* theme or even develop
your own custom theme. The theme is composed of four layers:

* favicon, logo and possible other graphical elements of the network using
  *nodewatcher* installation
* icons and other graphical elements to visualize *nodewatcher* elements
  (like nodes)
* SCSS files to generate CSS used for layout styling
* Django templates for XHTML layout

Favicon and Logo
----------------

Favicon and logo can be changed through settings. There are
``NETWORK_FAVICON_URL`` and ``NETWORK_LOGO_URL`` settings to set customized
favicon and logo URLs.

Overriding CSS
--------------

For small changes you might just want to override CSS in the browser, loading
your changes after the provided CSS files. So no changes to distributed files
are needed. You will just need to provide a ``head.html`` Django template file
which should then include your own CSS file. This file should be somewhere in
Django template search path, but before the distributed (empty) one.

You should use this approach really just for minor modifications. If you happen
to find yourself overriding a lot of CSS all around then this will probably be
unmaintainable in the future when distributed *nodewatcher* theme will change
and you will have to manually keep up with all the changes. In this it is best
to extend distributed *nodewatcher* theme through SCSS.

Changing CSS
------------

Color scheme and other styling modifications can be achieved by changing the
CSS of the theme. A new CSS style can be created using basic knowledge of
`CSS`_, however it is recommended that you first try to extend and modify an
existing basic theme. **Do not modify the actual CSS** in this case as it is
generated automatically using the `Compass`_ authoring framework. The source
SCSS files are located in the ``static/scss`` directory. One can check the
Compass `documentation`_ for more information about Compass.

.. _CSS: http://en.wikipedia.org/wiki/Cascading_Style_Sheet
.. _Compass: http://compass-style.org/
.. _documentation: http://compass-style.org/docs/

Assuming that you have now Compass installed on your system, here are the
instructions how to compile the default *nodewatcher* theme. Compass files are
organized into projects. To compile our project go to ``static/scss`` and
type::

    compass compile

This will update CSS files in ``statics/css``.

To use development settings (adds line comments with source information) use::

    compass compile -e development --force

During the actual development running this command may become annoying so the
handy way to compile CSS on the fly is to run the following command in a
separate terminal::

    compass watch -e development --force

In this case Compass will pool for changes to the source files and compile them
when needed. You can now focus solely on creating the theme.

It is recommended that you use our SCSS files as a base and extend them through
capabilities provided by Compass. So create your own Compass configuration file
and directory with SCSS files alongside the ``default`` directory and add your
changes there, using our files as a base.

SCSS Files
``````````

The syntax of the SCSS files is very similar to the one of the CSS, however,
there are some handy features that make development easier. Some basic examples
can be found `here`_ (note that there is also an older syntax called SASS that
should not be confused with SCSS). More examples on mixins provided by Compass
can be found `on a Compass website`_.

.. _here: http://sass-lang.com/
.. _on a Compass website: http://compass-style.org/docs/reference/compass/

Changing Django Templates
-------------------------

More drastic changes in layout can be made by modifying the Django templates.
In this case some knowledge of Django templating system is required. You can
then override specific template files from ``web/templates`` directory by
copying them in some other directory, modifying them and then adding the
directory path to the templates directory list ``TEMPLATE_DIRS`` in your
``settings.py`` file (before the default templates directory). Templates are
modular so it should be easy to change only parts you need.

Again, be careful not to change templates in a way to be hard to maintain them
with future *nodewatcher* versions. If you need more modular templates for your
needs, feel free to open a ticket with request.
