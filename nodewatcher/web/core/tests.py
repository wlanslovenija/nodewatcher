from django.utils import unittest
from core.allocation.pool import IpPool, IpPoolStatus

class IpPoolTestCase(unittest.TestCase):
  def setUp(self):
    """
    Prepare the IP pool test environment by creating some dummy IP
    pools.
    """
    self.pool = IpPool.objects.create(
      family = "ipv4",
      network = "10.10.0.0",
      prefix_length = 16,
    )

    self.small_pool = IpPool.objects.create(
      family = "ipv4",
      network = "192.168.1.0",
      prefix_length = 26,
    )

  def test_basic_allocation(self):
    # Test that we really get properly allocated objects
    a = self.pool.allocate_subnet(prefix_len = 27)
    b = self.pool.allocate_subnet(prefix_len = 27)
    c = self.pool.allocate_subnet(prefix_len = 26)

    # Test that something has been allocated
    self.assertNotEqual(a, None)
    self.assertNotEqual(b, None)
    self.assertNotEqual(c, None)

    # Test that we really have the right prefix lengths
    self.assertEqual(a.prefix_length, 27)
    self.assertEqual(b.prefix_length, 27)
    self.assertEqual(c.prefix_length, 26)

    # Test that distinct subnets have been allocated
    networks = set([a.network, b.network, c.network])
    self.assertEqual(len(networks), 3)

    # Test that statuses have been properly set
    self.assertEqual(a.status, IpPoolStatus.Full)
    self.assertEqual(b.status, IpPoolStatus.Full)
    self.assertEqual(c.status, IpPoolStatus.Full)

  def test_allocation_failure(self):
    # Test that we can't allocate more than we have
    a = self.small_pool.allocate_subnet(prefix_len = 24)
    self.assertEqual(a, None)

    # Test that we fail to get an allocation when the pool is exhausted
    a = self.small_pool.allocate_subnet(prefix_len = 27)
    b = self.small_pool.allocate_subnet(prefix_len = 27)
    c = self.small_pool.allocate_subnet(prefix_len = 27)
    self.assertNotEqual(a, None)
    self.assertNotEqual(b, None)
    self.assertEqual(c, None)