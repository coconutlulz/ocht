import unittest

from ..nodes.nodes import find_internal_nodes_num


class TestInternalNodesCounting(unittest.TestCase):
    sample_tree = [4, 2, 4, 5, -1, 4, 5]

    def test_empty_tree(self):
        tree = []
        self.assertEqual(find_internal_nodes_num(tree), 0)

    def test_only_roots_in_tree(self):
        tree = [-1] * 5
        self.assertEqual(find_internal_nodes_num(tree), 0)

    def test_sample_tree(self):
        self.assertEqual(find_internal_nodes_num(self.sample_tree), 3)

    def test_very_long_tree(self):
        self.assertEqual(find_internal_nodes_num(self.sample_tree * 100), 3)


if __name__ == '__main__':
    unittest.main()
