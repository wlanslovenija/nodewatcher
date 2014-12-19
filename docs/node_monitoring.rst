.. _registry-node-monitoring-schema:

Node Monitoring Schema
======================

Per-node monitoring schema in nodewatcher is built from various Django models and mixins,
using light extensions provided by the :ref:`registry-api`. This documentation specifies,
for each registry item identifier (see :ref:`registry-api-items`) the models that provide parts
of the final schema.

Each node is defined as an instance of :class:`nodewatcher.core.models.Node` and represents a
network-connected device that may be managed by nodewatcher. The model instance itself only provides
a universally unique identifier (UUID) and has no other attributes. All monitoring attributes
are added by various models through the use of the registry.

core.general
------------

.. autoclass:: nodewatcher.core.monitor.models.GeneralMonitor()

core.interfaces
---------------

.. autoclass:: nodewatcher.core.monitor.models.InterfaceMonitor()

.. autoclass:: nodewatcher.core.monitor.models.WifiInterfaceMonitor()

core.interfaces.network
-----------------------

.. autoclass:: nodewatcher.core.monitor.models.NetworkAddressMonitor()

system.status
-------------

.. autoclass:: nodewatcher.core.monitor.models.SystemStatusMonitor()

system.resources.general
------------------------

.. autoclass:: nodewatcher.core.monitor.models.GeneralResourcesMonitor()

system.resources.network
------------------------

.. autoclass:: nodewatcher.core.monitor.models.NetworkResourcesMonitor()

network.routing.topology
------------------------

.. autoclass:: nodewatcher.core.monitor.models.RoutingTopologyMonitor()

.. autoclass:: nodewatcher.core.monitor.models.TopologyLink()

.. autoclass:: nodewatcher.modules.routing.olsr.models.OlsrRoutingTopologyMonitor()
   :show-inheritance:

network.routing.announces
-------------------------

.. autoclass:: nodewatcher.core.monitor.models.RoutingAnnounceMonitor()

network.measurement.rtt
-----------------------

.. autoclass:: nodewatcher.core.monitor.models.Measurement()

.. autoclass:: nodewatcher.core.monitor.models.RttMeasurementMonitor()
   :show-inheritance:

network.clients
---------------

.. autoclass:: nodewatcher.core.monitor.models.ClientMonitor()

.. autoclass:: nodewatcher.core.monitor.models.ClientAddress()
