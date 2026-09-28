import os
import unittest

from relative_path_resolver import relative_path, common_ancestor, DifferentRootError


class RelativePathTests(unittest.TestCase):
    def test_descend(self):
        self.assertEqual(relative_path('/a', '/a/b/c'), os.path.join('b', 'c'))

    def test_ascend(self):
        self.assertEqual(relative_path('/a/b', '/a'), '..')

    def test_sibling(self):
        self.assertEqual(relative_path('/a/b', '/a/c'), os.path.join('..', 'c'))

    def test_same_dir(self):
        self.assertEqual(relative_path('/a/b', '/a/b'), '.')

    def test_cross_branch(self):
        self.assertEqual(
            relative_path('/a/b/c', '/a/x/y'),
            os.path.join('..', '..', 'x', 'y')
        )

    def test_trailing_slash_ignored(self):
        self.assertEqual(relative_path('/a/b/', '/a/c/'), os.path.join('..', 'c'))

    def test_dot_segments_normalized(self):
        self.assertEqual(relative_path('/a/./b', '/a/c'), os.path.join('..', 'c'))

    def test_parent_segments_normalized(self):
        self.assertEqual(relative_path('/a/b/../c', '/a/x'), os.path.join('..', 'x'))

    def test_relative_paths_share_root(self):
        self.assertEqual(relative_path('a/b', 'a/c'), os.path.join('..', 'c'))

    def test_relative_paths_no_common_prefix(self):
        # Both relative, no shared leading component — still valid because
        # they share the (empty) relative root.
        self.assertEqual(relative_path('a', 'b'), os.path.join('..', 'b'))

    def test_different_roots_raise(self):
        with self.assertRaises(DifferentRootError):
            relative_path('/a', 'C:\\b')


class CommonAncestorTests(unittest.TestCase):
    def test_parent(self):
        self.assertEqual(common_ancestor('/a/b', '/a/c'), '/a')

    def test_self(self):
        self.assertEqual(common_ancestor('/a/b', '/a/b'), '/a/b')

    def test_no_common(self):
        self.assertEqual(common_ancestor('/a', '/b'), '')

    def test_different_roots(self):
        self.assertEqual(common_ancestor('/a', 'C:\\b'), '')


if __name__ == '__main__':
    unittest.main()
