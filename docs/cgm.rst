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

Build channels enable having multiple builders with different versions of source code.
That way testing of newer source code can be done without changes to default build channel.
Build channel can be selected in Node settings.

.. _cgm-build-version:

Build Version
-------------

Firmware image build version is equal to source code version included in builders.
Version can only be bumped with generating new builders with never source code.

.. _cgm-builders:

Builders
--------

Builders are docker images used for firmware image generation.
Builders are platform and architecture specific.
Builders can be custom generated or periodicly released docker builder images for supported platforms can be used.
In order to be used in Nodewatcher builders need to be linked either by passing --link argument or by editing docker-compose.yml. 
Instructions for custom generating builders can be found here: https://github.com/wlanslovenija/firmware-core

.. _cgm-platforms:

Platforms
---------

Nodewatcher platform descriptors are defined in ``nodewatcher/modules/platforms`` and are Python modules.
Platform descriptors define way that firmware images are generated.
Currently supported platforms are OpenWRT and LEDE.
Suport for new platforms can be done by extending existing descriptors if your platform is based on OpenWRT or make a new one that suits your platform.

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
  Each switch is identified by its logical identifier, which is platform-independent (eg. ``switch0``). Each
  switch can also define multiple VLAN presets that can be used when configuring the switch. If the switch supports
  custom configuration, it should have the ``configurable`` attribute set to ``True``.

* ``ports`` contains a list of ethernet ports, which describe physical ethernet ports. Each port is identified by
  its logical identifier, which is platform-independent (eg. ``wan0``, ``lan0``, etc.).

* ``port_map`` contains the mapping of logical port names to platform-specific identifiers (one mapping per platform,
  eg. OpenWrt). It maps all platform-independent identifiers (eg. ``wifi0``, ``switch0``, ``wan0``, ``lan0``) to
  identifiers used on a specific platform (eg. ``radio0``, ``switch0``, ``eth1``, ``eth0``). For switch configurations
  a special ``SwitchPortMap`` instance may be used to define VLAN interface naming.

* ``drivers`` defines the drivers used by the radios on each platform. For example, on OpenWrt this may be ``mac80211``.

* ``profiles`` define the platform-specific device profiles that should be used when building an image and paths to the
  resulting firmware files. Note that a single profile may be used for multiple devices. For example, on OpenWrt a
  profile ``TLWR741`` generates a firmware file ``openwrt-ar71xx-generic-tl-wr741nd-v1-squashfs-factory.bin`` for
  the TP-Link WR741NDv1 device and this must be configured here. The firmware filenames can also contain filename
  patterns containing ``?`` and ``*`` to match different filenames at once.

The best way to determine the values for ``radios``, ``switches``, ``ports``, ``port_map`` and ``drivers`` is
to boot a stock version of OpenWrt on the device and check the default configuration inside ``/etc/config/network``
and ``/etc/config/wireless``.

OpenWrt profiles may be listed by running ``make info`` on the `generated image builder`_.
LEDE profiles can be made by mostly replacing OpenWRT with LEDE.
.. _generated image builder: https://github.com/wlanslovenija/firmware-core#building-images
