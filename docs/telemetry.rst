Telemetry
=========

The telemetry provider component enables any node to report its operational
attributes via a simple HTTP-based hierarchical key-value format. Provider
is split into multiple OpenWrt packages as follows:

* ``nodewatcher-core`` provides the basic framework for developing telemetry
  modules, it is required by all other packages.
* ``nodewatcher-clients`` provides client-related monitoring (in combination
  with ``nodogsplash`` and ``olsr-mod-actions`` plugin).
* ``nodewatcher-watchdog`` is responsible for performing periodic testing of
  node's network sanity and for attempting to recover from weird situations.
* ``nodewatcher-solar`` provides power regulator telemetry via the solar package.
* ``nodewatcher-digitemp`` provides 1-wire thermometer telemetry via the digitemp
  package.

Installation
------------

Installing these packages should be just a matter of adding our repository to
``/etc/opkg.conf``::

     src/gz wlansi http://bindist.wlan-si.net/profiles/PLATFORM

where PLATFORM is one of the supported platforms (currently ``atheros``, ``brcm24``
and ``ar71xx``). Then installing packages should be just a matter of an ``opkg install``.

Structure
---------

Remote invocation scripts are installed into ``/www/cgi-bin`` and should be
accessible via HTTP URL in the form of ``http://x.y.z.w/cgi-bin/nodewatcher``
(where ``x.y.z.w`` is the node's primary IP address).

Individual telemetry modules are installed into ``/etc/nodewatcher.d``, there
is also an example module available in our repository (note that this module
is not installed).

Format
------

The format used by our provider is a simple text format. Lines starting with a
semicolon (``;``) are comments and should be ignored by parsers. Any non-comment
line is composed of two parts separated by the first left-wise colon (``:``). Left
part is denoted as key and the right part as value.

All keys form a hierarchy. Namespace atoms are ASCII strings that match the regular
expressions based on their position in the hierarchy:

* Top-level namespace atoms must match ``[A-Za-z-]+``. In addition, if a top-level
  namespace atom contains a capital letter from the range A-Z, the whole atom must
  be capitalized. Capitalized top-level atoms are reserved for internal use.
* Namespace atoms on lower levels must match ``[a-z0-9-]+``.

Each key may contain multiple namespace atoms separated by dots (``.``), for example
a valid key is ``wireless.radios.ath0.bssid``. The format of value is currently not
defined and should be considered of a per-key type defined by the module that outputs
it. Value must not contain a newline, as newlines separate key-value pairs.

Currently the only special namespace is ``META``. It contains information about installed
modules and their versions. This information is available in ``META.modules.*.serial``
and is of integer type. Dots in module names are replaced with dashes (``-``) when
they are used as namespace atoms.

In the future this hierarchical namespace will be centrally allocated to individual
*nodewatcher* telemetry providers, but currently the allocations are ad-hoc and may change.

Example
-------

The following is an example of nodewatcher output from one of the nodes::

    ;
    ; nodewatcher monitoring system
    ;
    META.version: 2
    META.modules.core-clients.serial: 1
    iptables.redirection_problem: 0
    net.losses: 0
    META.modules.core-general.serial: 1
    general.uuid: 7061c9ab-2bcc-442e-b0bc-d9959b519e75
    general.version: hg
    general.local_time: 43987
    general.uptime: 43987.78 41507.07
    general.loadavg: 0.25 0.27 0.30 1/39 523
    general.memfree: 14056
    general.buffers: 1496
    general.cached: 5044
    META.modules.core-traffic.serial: 1
    iface.eth0.down: 0
    iface.eth0.up: 0
    iface.eth1.down: 0
    iface.eth1.up: 0
    iface.wlan0.down: 73108492
    iface.wlan0.up: 23656806
    iface.edge0.down: 0
    iface.edge0.up: 1909300
    META.modules.core-vpn.serial: 1
    net.vpn.upload_limit: 
    net.vpn.mac: 
    META.modules.core-wireless.serial: 1
    wireless.radios.wlan0.bssid: 02:CA:FF:EE:BA:BE
    wireless.radios.wlan0.essid: open.wlan-si.net
    wireless.radios.wlan0.frequency: 2.447
    wireless.radios.wlan0.mac: 54:E6:FC:F3:7F:54
    wireless.radios.wlan0.rts: off
    wireless.radios.wlan0.frag: off
    wireless.radios.wlan0.bitrate: 
    wireless.radios.wlan0.signal: 0
    wireless.radios.wlan0.noise: 0
    wireless.errors: 0
    wifi.bssid: 02:CA:FF:EE:BA:BE
    wifi.essid: open.wlan-si.net
    wifi.frequency: 2.447
    wifi.mac: 54:E6:FC:F3:7F:54
    wifi.rts: off
    wifi.frag: off
    wifi.bitrate: 
    wifi.signal: 0
    wifi.noise: 0
    wifi.errors: 0

