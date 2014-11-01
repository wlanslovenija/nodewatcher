.. _resources:

Resources
=========

TODO.

Mixins
------

TODO.

.. autoclass:: nodewatcher.core.allocation.ip.models.IpAddressAllocator()

   :param family: Address family.
   :type family: string

   :param pool: Reference to the allocation pool that this resource will be allocated from.
   :type pool: foreign key to :class:`~nodewatcher.core.allocation.ip.models.IpPool`

   :param prefix_length: Prefix length.
   :type prefix_length: int

   :param allocation: Reference to the actual allocation that has been allocated from the
     configured pool.
   :type allocation: foreign key to :class:`~nodewatcher.core.allocation.ip.models.IpPool`
