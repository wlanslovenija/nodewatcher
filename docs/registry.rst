Registry
========

The concept of modularity brings new challenges to the *nodewatcher* platform. Foremost, a question poses itself: how to enable modules to add their own configuration options to registered nodes. The platform has to provide interfaces for:

* Persistent storage of configuration data, where schema is defined by module developer.
* Ability to automatically generate forms from the schema, so that the developer does not need to define the forms manually.
* Validation of all data at entry time in broader context of node configuration: one configuration value could have dependencies on other modules which require suitable validation at value change. Furthermore, to satisfy the needs of the firmware generator, we wanted to assure that user gets feedback about possible invalid configuration for particular hardware immediately, so that she can correct the error directly, and not just after firmware generator fails at some later stage.
* Specification of context-sensitive default configuration values. For example: *node in project X has in the case that hardware supports multiple SSID on interface of ad-hoc type by default SSID "mesh.wlan-si.net", otherwise, in the case hardware supports only one SSID, the default should be "open.wlan-si.net"*.

To cover all the requirements listed above we developed a component named registry. It is a thin layer above existing Django ORM which allows defining schemata, automatic generation of corresponding configuration forms, setup of default configuration and validation of provided schema. Furthermore, hierarchical relations between elements are supported, too (eg. one radio can have multiple interfaces which can in turn have multiple addresses) which is a challenge especially when generating suitable user interface and rules evaluation.

Extending and adding functionalities is possible at multiple points so that, for example, developer can change how forms behave (which can dynamically adapt to values of other fields). It is possible at successful validation of configuration to execute various actions (eg. automatic IP addresses allocation based on selected requests, or validation configuration for particular hardware in the case of the firmware generation).

*nodewatcher* 3.0 uses this component for storing logs about nodes and for extracting configuration for all other modules (firmware generator, network monitoring, etc.).

Basic Registry Structure
-----------------------

TODO

Registration Points in nodewatcher
----------------------------------

Core nodewatcher platform currently provides the following two registration points:

* ``node.config`` attached to the ``Node`` model. This registration point holds all per-node configuration models that the modules provide. TODO: link to schema
* ``node.monitoring`` attached to the ``Node`` model. This registration point holds all per-node monitoring models that the modules provide. TODO: link to schema

Queryset Extensions
-------------------

Registration points extend the object manager of the class their are attached to. Additional methods are provided so that you can directly query the registry hierarchy. Since multiple registration points can be attached to the same model a registration point must first be selected before making any queries. This can be done by using the ``regpoint`` method as follows::

    Node.objects.regpoint('config')

Since instances of ``Node`` themselves don't have any fields besides the UUID you have to join them with registry models in order to obtain the required data. In order to make this easier, a ``registry_fields`` method is provided on the query set::

    Node.objects.regpoint('config').registry_fields(
        name='core.general#name',
        type='core.type#type',
        router_id='core.routerid#router_id',
        project='core.project#project.name',
    ).regpoint('monitoring').registry_fields(
        last_seen='core.general#last_seen',
    )

The resulting ``Node`` (actually the results will be instances of a special proxy class called ``NodeRegistryProxy``, because we cannot modify fields in the existing model class) instances will have additional fields called ``name``, ``type``, ``router_id``, ``project`` and ``last_seen`` that will have the values of their respective registry models. Values for these fields will be obtained by performing joins with tables of the registry item models that provide these fields. Note that multiple models may be registered under the same registry identifier (for example ``core.general`` in the above case actually has ``GeneralConfig`` and ``CgmGeneralConfig`` registered). In such cases all models will be traversed and the one providing field ``name`` will be selected for joining (again, in the above case this would correspond to ``GeneralConfig``).

Similarly, you can use registry fields in filter expressions using ``registry_filter`` method::

    Node.objects.regpoint('config').registry_filter(
        core_general__name='test-4',
    )

The same rule as above applies for model resolution.
