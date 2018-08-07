API v2
======

The latest nodewatcher version uses API v2. Unlike v1 there is more control over which data is shown. In all of the examples below the wlan-si nodewatcher page is used for easier presentation. If you intend to use this on your own server replace the https://nodes.wlan-si.net with the address of your server. When you go to the API page in nodewatcher:

https://nodes.wlan-si.net/api/v2/

You are presented with certain groups of data:

* ``pool/ip`` https://nodes.wlan-si.net/api/v2/pool/ip/
* ``statistics/device`` https://nodes.wlan-si.net/api/v2/statistics/device/
* ``link`` https://nodes.wlan-si.net/api/v2/link/
* ``node`` https://nodes.wlan-si.net/api/v2/node/
* ``project`` https://nodes.wlan-si.net/api/v2/project/
* ``statistics/project`` https://nodes.wlan-si.net/api/v2/statistics/project/
* ``statistics/status`` https://nodes.wlan-si.net/api/v2/statistics/status/
* ``unknown_node`` https://nodes.wlan-si.net/api/v2/unknown_node/
* ``user_authentication_key`` https://nodes.wlan-si.net/api/v2/user_authentication_key/
* ``event`` https://nodes.wlan-si.net/api/v2/event/
* ``warning`` https://nodes.wlan-si.net/api/v2/warning/
* ``build_result`` https://nodes.wlan-si.net/api/v2/build_result/

Querying data
-------------

We are going to focus on the ``node`` aspect. Some of the main features of requesting data through the API are:

* ``format``
* ``limit``
* ``offset``
* ``fields``
* ``filters``

Each option that you want to add to the API request is given in the query string (after the '?').

Format
------

``format`` allows you to represent the gathered data in JSON format:

https://nodes.wlan-si.net/api/v2/node/?format=JSON

Limit
-----

``limit`` helps you to set an exact number of nodes that you want to show per page.

https://nodes.wlan-si.net/api/v2/node/?limit=1

This will give you a list of all registered nodes with each node on a single page.

Offset
------

``offset`` allows you to go to a specific page of the API request. This alongside limit can allow you to show data for a certain node or set of nodes.

https://nodes.wlan-si.net/api/v2/node/?offset=17

Fields
------

When you make a simple API request like this https://nodes.wlan-si.net/API/v2/node/ you can see that there isn't much information for each of the nodes. That is because node data is divided in ``fields`` and you need to specify each ``field`` that you want to access. There are 2 groups ``config`` and ``monitoring``:

* **config:**
    * core.general
    * core.type
    * core.project
    * core.description
    * core.location
    * core.routerid
    * core.authentication
    * core.roles
    * core.switch
    * core.switch.vlan
    * core.interfaces
    * core.interfaces.network
    * core.interfaces.limits
    * core.servers.dns
* **monitoring:**
    * core.general
    * core.interfaces
    * core.interfaces.network
    * system.status
    * system.resources.general
    * system.resources.network
    * network.routing.topology
    * network.routing.announces
    * network.measurement.rtt
    * network.clients

You can read more about node configuration and monitoring here:

http://docs.nodewatcher.net/en/development/node_config.html
http://docs.nodewatcher.net/en/development/node_monitoring.html

These are 2 simple examples of how to select certain ``fields``:

https://nodes.wlan-si.net/api/v2/node/?fields=config:core.general
https://nodes.wlan-si.net/api/v2/node/?fields=monitoring:core.interfaces

You can also have multiple ``fields`` in a single request:

https://nodes.wlan-si.net/api/v2/node/?fields=config:core.general&fields=monitoring:core.interfaces

Filters
-------

``filter`` as the name says is used to filter the requested data. It can be used in 2 ways: to filter data that is exactly the same as the given value or to filter data that contains the given value.

This example will give you all nodes whose name is mp and if you try it out you will see that there aren't any nodes with that name:

https://nodes.wlan-si.net/api/v2/node/?filters=config:core.general__name="mp"

But if you add the ``__contains`` parameter you will see that now you will get all the nodes that contain "mp" in their name: 

https://nodes.wlan-si.net/api/v2/node/?filters=config:core.general__name__contains="mp"


.. note:: All of these query parameters can be used together by adding '&' between each of them.

Examples
--------

Node name
.........

Getting a node name with given node id:

https://nodes.wlan-si.net/api/v2/node/node_id/?fields=config:core.general__name

As you can see accessing individual parts of the ``config:core.general`` or any other field can be done by adding the name of the wanted part after ``__``, like ``__name``.

Multiple filters
................

Applying multiple filters at the same time:

https://nodes.wlan-si.net/api/v2/node/node_id/?filters=monitoring:core.general__name__contains="test",monitoring:core.general__name__contains="mp"

Multiple filters can be applied by separating each one of them with ','.

Time filtering
..............

There are some filtering options available for certain fields. Filtering by ``last_seen`` can be done by giving a ``__gt`` (greater than) or ``__lt`` (lower than) value:

https://nodes.wlan-si.net/api/v2/node/node_id/?filters=monitoring:core.general__last_seen__gt="2016-05-21T13:17:27.226815Z"

This will show all nodes that have the ``last_seen`` value greater than ``2016-05-21T13:17:27.226815Z``.