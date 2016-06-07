.. _firmware-image-generation:

Firmware Image Generation
=========================

TODO.

Configuration Generating Modules
--------------------------------

TODO.

.. _cgm-build-channel:

Build Channel
-------------

TODO.

.. _cgm-build-version:

Build Version
-------------

TODO.

.. _cgm-platforms:

Platforms
---------

TODO.

.. _cgm-devices:

Device Descriptors
------------------

Nodewatcher device descriptors are defined in ``nodewatcher/modules/devices`` and are normal Python modules.
The best way to define a new descriptor is to extend an already existing one. This can be done if a similar
device is already supported (has a descriptor) and you just need to modify some minor things.
In this case your new descriptor may simply extend an existing one using Python class inheritance and omit
some of the attributes. In any case identifier and name must be defined (and be unique).

The following things need to be determined for a device descriptor:

* ``identifier`` is an all-lowercase unique device identifier, which should consist of a manufacturer prefix,
  a model identifier and a version.

* ``name`` is a human-readable device name consisting of a model identifier and a version.
  It should not contain a manufacturer name.

* ``manufacturer`` is a human-readable manufacturer name.

* ``url`` is an URL containing more information about the device.

* ``architecture`` identifies the OpenWrt architecture that the device needs (eg. ``ar71xx``).

* ``antennas`` is a list of antenna descriptors, which describe physical antennas attached to the device by default.

* ``radios`` is a list of radio descriptors, which describe radios present on the device. Each radio specifies the
  protocols that it supports, antennas that it has attached and features that it supports. Each radio is identified
  by its logical identifier, which is platform-independent (eg. ``wifi0``).

* ``switches`` contains a list of switch descriptors, which describe ethernet switches present on the device.
  Each switch is identified by its logical identifier, which is platform-independent (eg. ``switch0``).

* ``ports`` contains a list of ethernet ports, which describe either physical ethernet ports or a configuration of
  switched ethernet ports present on the device. Each port is identified by its logical identifier, which is
  platform-independent (eg. ``wan0``, ``lan0``, etc.).

* ``port_map`` contains the mapping of logical port names to platform-specific identifiers (one mapping per platform,
  eg. OpenWrt). It maps all platform-independent identifiers (eg. ``wifi0``, ``switch0``, ``wan0``, ``lan0``) to
  identifiers used on a specific platform (eg. ``radio0``, ``switch0``, ``eth1``, ``eth0``).

* ``drivers`` defines the drivers used by the radios on each platform. For example, on OpenWrt this may be ``mac80211``.

* ``profiles`` define the platform-specific device profiles that should be used when building an image and paths to the
  resulting firmware files. Note that a single profile may be used for multiple devices. For example, on OpenWrt a
  profile ``TLWR741`` generates a firmware file ``openwrt-ar71xx-generic-tl-wr741nd-v1-squashfs-factory.bin`` for
  the TP-Link WR741NDv1 device and this must be configured here.

The best way to determine the values for ``radios``, ``switches``, ``ports``, ``port_map`` and ``drivers`` is
to boot a stock version of OpenWrt on the device and check the default configuration inside ``/etc/config/network``
and ``/etc/config/wireless``.

OpenWrt profiles may be listed by running ``make info`` on the `generated image builder`_.

.. _generated image builder: https://github.com/wlanslovenija/firmware-core#building-images
