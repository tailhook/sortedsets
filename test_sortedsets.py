import unittest

from sortedsets import SortedSet


class TestSortedSets(unittest.TestCase):

    def test_simple(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        self.assertEqual(ss['one'], 1)
        self.assertEqual(ss['two'], 2)

    def test_keys(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        self.assertEqual(list(ss), [
            'one',
            'two',
            ])
        self.assertEqual(list(ss.keys()), [
            'one',
            'two',
            ])

    def test_items(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        self.assertEqual(list(ss.items()), [
            ('one', 1),
            ('two', 2),
            ])

    def test_values(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        self.assertEqual(list(ss.values()), [1, 2])


if __name__ == '__main__':
    unittest.main()
