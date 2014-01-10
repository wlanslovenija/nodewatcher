Schema
======

.. warning::

    This is an **incomplete** database schema for *nodewatcher*. Current schema summary only describes some
    monitoring-related data -- image generator profiles (configuration) is not documented at this moment.

Node
----

Each node is represented as an instance of model Node. A node may be in any of multiple states
(depending on factors specified by the monitoring system):

* **Invalid** -- Node is visible in the routing tables, but is not known to *nodewatcher*
  (entries with this status are temporary and are removed as soon as a node is not visible anymore).
  Any other status means that the node is known to *nodewatcher*.

* **Up** -- Node is visible in the routing tables and has replied to at least one ICMP ECHO probe
  (there were no duplicate packets received).

* **Visible** -- Node is visibile in the routing tables but has not replied to any ICMP ECHO probes.

* **Duped** -- Node is visible in the routing tables and has replied to at least one ICMP ECHO probe
  twice with the same sequence number.

* **Down** -- Node is not visible in the routing tables.

* **Pending** -- Node has not yet been seen in the routing tables since its registration with the *nodewatcher*.

In the monitoring subsystem, a node is identified by its ``ROUTER-ID`` within the mesh. Currently this is the
main IPv4 address for the node. Each node also carries a UUID that is used as primary node identifier as it
is persistent across node IP changes.

.. |br| raw:: html

   <br />

Schema is as follows:

+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| Field               | Modifiers            | Description                                                                                              |
+=====================+======================+==========================================================================================================+
| uuid                | primary key          | unique node identifier (Version 4 UUID as per RFC 4122)                                                  |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ip                  | unique |br| observed | contains the ``ROUTER-ID`` for this node                                                                 |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| name                | unique               | human readable node name, must be a valid DNS hostname                                                   |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| owner               |                      | node maintainer                                                                                          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| location            |                      | human readable node location                                                                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| project             |                      | project that this node belongs to (projects also define IP pools and DNS zones)                          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| notes               |                      | maintainer-specific notes                                                                                |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| url                 |                      | URL containing further information about the node (usually pictures of node's view)                      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| geo_lat             |                      | latitude (in decimal degrees)                                                                            |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| geo_long            |                      | longitude (in decimal degrees)                                                                           |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ant_external        |                      | a boolean flag indicating that an external antenna is being used by the node                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ant_polarization    |                      | enumeration of following values:                                                                         |
|                     |                      |                                                                                                          |
|                     |                      | * *Unknown* -- polarization is not known                                                                 |
|                     |                      | * *Horizontal* -- horizontal polarization                                                                |
|                     |                      | * *Vertical* -- vertical polarization                                                                    |
|                     |                      | * *Circular* -- circular polarization                                                                    |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ant_type            |                      | enumeration of following values:                                                                         |
|                     |                      |                                                                                                          |
|                     |                      | * *Unknown* -- antenna type is not known                                                                 |
|                     |                      | * *Omni* -- an omni-directional antenna                                                                  |
|                     |                      | * *Sector* -- a sector antenna                                                                           |
|                     |                      | * *Directional* -- a directional antenna                                                                 |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| system_node         |                      | a boolean flag indicating that this node provides core mesh services (like root DNS, NTP, etc.)          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| border_router       |                      | a boolean flag indicating that this node is a border router, that is it may redistribute external routes |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| node_type           |                      | enumeration of following values:                                                                         |
|                     |                      |                                                                                                          |
|                     |                      | *Server* -- this type is usually used for non wifi nodes                                                 |
|                     |                      | *Mesh* -- a standard wifi mesh router                                                                    |
|                     |                      | *Test* -- testing node that is even more experimental than others                                        |
|                     |                      | *Unknown* -- nodes with ``Invalid`` state                                                                |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| redundancy_link     | observed             | a boolean flag indicating whether this node has a redundant VPN link to the mesh                         |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| redundancy_req      |                      | a boolean flag indicating whether the lack of a redundant VPN link should trigger a warning message      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| conflicting_subnets | observed             | a boolean flag indicating whether any of the node's subnets are currently in conflict                    |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| warnings            | observed             | a boolean flag indicating whether warning messages are present for this node                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| status              | observed             | previously mentioned node status                                                                         |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| peers               | observed             | number of active node peers according to mesh topology                                                   |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| peer_list           | observed             | many to many relation of peer links                                                                      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| last_seen           | observed             | timestamp when node was last seen                                                                        |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| first_seen          | observed             | timestamp when node was first seen                                                                       |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| wifi_mac            | observed             | wifi interface MAC address                                                                               |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| vpn_mac             | observed             | VPN interface MAC address (observed)                                                                     |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| vpn_mac_conf        |                      | VPN interface MAC address (configured)                                                                   |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| channel             | observed             | currently used wifi channel                                                                              |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| rtt_min             | observed             | RTT measurement                                                                                          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| rtt_avg             | observed             | RTT measurement                                                                                          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| rtt_max             | observed             | RTT measurement                                                                                          |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| pkt_loss            | observed             | packet loss                                                                                              |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| firmware_version    | observed             | firmware version used on the node                                                                        |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| bssid               | observed             | node's BSSID                                                                                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| essid               | observed             | node's ESSID                                                                                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| local_time          | observed             | local node's time                                                                                        |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| clients             | observed             | number of clients connected via nodogsplash                                                              |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| clients_so_far      | observed             | cumulative number of clients so far                                                                      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| uptime              | observed             | current node's system uptime (not network connectivity) in seconds                                       |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+

Modifier description:

* *primary key* -- this field is a primary identifier for the given node
* *unique* -- this field must be unique among all nodes
* *observed* -- this field is updated by the monitoring system

Link
----

Links represent topological connections between nodes as reported by the routing daemon. Each link has the following schema:

+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| Field               | Modifiers            | Description                                                                                              |
+=====================+======================+==========================================================================================================+
| src                 | observed             | source node                                                                                              |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| dst                 | observed             | destination node                                                                                         |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| lq                  | observed             | link quality                                                                                             |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ilq                 | observed             | inverse link quality                                                                                     |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| etx                 | observed             | routing metric (these fields are currently as reported by OLSR routing daemon and are probably           |
|                     |                      | routing-protocol specific)                                                                               |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+

All links are of temporary nature and are kept in sync with routing topology updates.

Subnet
------

Each announced and/or registered IP subnet is represented in the database schema
by the Subnet model. A subnet may be in any of multiple states (depending on
factors specified by the monitoring system):

* **AnnouncedOk** -- subnet is known to *nodewatcher* and is allocated to the node that is currently announcing it.

* **NotAnnounced** -- subnet is known to *nodewatcher*, allocated to a specific node but the node that the subnet
  is allocated to is not announcing it at the moment.

* **NotAllocated** -- subnet is not known to *nodewatcher*, but a node is announcing it anyway.

* **Subset** -- subnet is a more specific announce of a node's subnet that has status ``AnnouncedOk`` (subnet entries
  with this status are only temporary - they are present as long as they are seen in the routing tables and are treated
  the same as ``AnnouncedOk``).

* **Hijacked** -- subnet is known to *nodewatcher* but is being announced by some node other than that to which the
  subnet has been allocated.

Subnet schema is as follows:

+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| Field               | Modifiers            | Description                                                                                              |
+=====================+======================+==========================================================================================================+
| node                | observed             | node the subnet belongs to                                                                               |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| subnet              | observed             | textual representation of the subnet                                                                     |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| cidr                | observed             | subnet prefix length                                                                                     |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| description         |                      | description which may be specified by the user                                                           |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| allocated           |                      | a boolean flag specifying whether this has been allocated via *nodewatcher* databse                      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| allocated_at        |                      | allocation timestamp                                                                                     |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| status              | observed             | previously mentioned subnet state                                                                        |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| last_seen           | observed             | timestamp when subnet was last seen                                                                      |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+
| ip_subnet           | ip field             | bitwise representation of the subnet for r-tree optimized subnet queries (used for conflict detection)   |
+---------------------+----------------------+----------------------------------------------------------------------------------------------------------+

Modifier description:

* *ip field* -- this field is a special r-tree indexed field implemented by the IP4R_ PostgreSQL extension

.. _IP4R: http://pgfoundry.org/projects/ip4r/
