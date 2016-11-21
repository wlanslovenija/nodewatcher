import unittest

from nodewatcher.utils import datastructures


class DatastructuresTest(unittest.TestCase):
    def test_merge_dict(self):
        result = datastructures.merge_dict({'a': 10, 'b': 20}, {'a': 42, 'c': 'hello'})
        self.assertEqual(result, {'a': 42, 'b': 20, 'c': 'hello'})

        result = datastructures.merge_dict({'a': {'b': 1, 'c': 2, 'd': {'e': 1}}}, {'a': {'foo': 1, 'd': {'f': 10}}})
        self.assertEqual(result, {'a': {'b': 1, 'c': 2, 'd': {'e': 1, 'f': 10}, 'foo': 1}})
