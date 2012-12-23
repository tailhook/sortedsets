import unittest
import random
import copy
import fractions
from operator import itemgetter
from itertools import combinations, product
from unittest.mock import patch

from sortedsets import SortedSet


class TestSortedSets(unittest.TestCase):

    def test_simple(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        self.assertEqual(ss['one'], 1)
        self.assertEqual(ss['two'], 2)

    def test_index(self):
        ss = SortedSet({
            'one': 1,
            'two': 2,
            })
        self.assertEqual(ss.index('two'), 1)
        self.assertEqual(ss.index('one'), 0)

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

    def test_negative(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = -2
        self.assertEqual(ss['one'], 1)
        self.assertEqual(ss['two'], -2)
        self.assertEqual(list(ss), ['two', 'one'])
        self.assertEqual(ss.index('two'), 0)
        self.assertEqual(ss.index('one'), 1)

    def test_floats(self):
        ss = SortedSet()
        # we use values that have exact representation as floating point number
        ss['one'] = 1.25
        ss['two'] = 1.5
        ss['three'] = -3.0
        self.assertEqual(ss['one'], 1.25)
        self.assertEqual(ss['two'], 1.5)
        self.assertEqual(ss['three'], -3.0)
        self.assertEqual(list(ss), ['three', 'one', 'two'])

    def test_fractions(self):
        ss = SortedSet()
        # we use values that have exact representation as floating point number
        ss['one'] = fractions.Fraction(1, 2)
        ss['two'] = fractions.Fraction(2, 3)
        ss['three'] = fractions.Fraction(-3, 2)
        self.assertEqual(ss['one'], fractions.Fraction(1, 2))
        self.assertEqual(ss['two'], fractions.Fraction(2, 3))
        self.assertEqual(ss['three'], fractions.Fraction(-3, 2))
        self.assertEqual(list(ss), ['three', 'one', 'two'])

    def test_delete(self):
        ss = SortedSet()
        ss['one'] = 1
        ss['two'] = 2
        ss['three'] = 3
        del ss['two']
        self.assertEqual(ss['one'], 1)
        self.assertEqual(ss['three'], 3)
        self.assertEqual(list(ss), ['one', 'three'])

    def test_key_by_index(self):
        ss = SortedSet({
            'one': 1,
            'two': 2,
            })
        self.assertEqual(ss.by_index[1], 'two')
        self.assertEqual(ss.by_index[0], 'one')

    def test_repr(self):
        ss = SortedSet({
            'one': 1,
            'two': 2,
            })
        self.assertEqual(repr(ss), "<SortedSet {'one': 1, 'two': 2}>")

    def test_slice_by_index(self):
        data = {
            'one': 1,
            'two': 2,
            }
        ss = SortedSet(data)
        self.assertEqual(ss.by_index[:], SortedSet(data))
        self.assertEqual(ss.by_index[1:], SortedSet({'two': 2}))
        self.assertEqual(ss.by_index[2:], SortedSet())
        self.assertEqual(ss.by_index[3:], SortedSet())
        self.assertEqual(ss.by_index[:-1], SortedSet({'one': 1}))
        self.assertEqual(ss.by_index[:-2], SortedSet())
        self.assertEqual(ss.by_index[:-3], SortedSet())
        self.assertEqual(ss.by_index[:-4], SortedSet())
        with self.assertRaises(ValueError):
            ss.by_index[::0]
        with self.assertRaises(ValueError):
            ss.by_index[::-1]
        with self.assertRaises(ValueError):
            ss.by_index[::-2]

    def test_slice_by_score(self):
        data = {
            'one': 1,
            'two1': 2,
            'two2': 2,
            'two3': 2,
            'three': 3,
            }
        ss = SortedSet(data)
        self.assertEqual(ss.by_score[:], SortedSet(data))
        self.assertEqual(ss.by_score[1:], SortedSet(data))
        self.assertEqual(ss.by_score[1:4], SortedSet(data))
        self.assertEqual(ss.by_score[:4], SortedSet(data))
        tmp = data.copy()
        del tmp['one']
        self.assertEqual(ss.by_score[1.5:], SortedSet(tmp))
        self.assertEqual(ss.by_score[2:], SortedSet(tmp))
        self.assertEqual(ss.by_score[2:4], SortedSet(tmp))
        self.assertEqual(ss.by_score[1.5:4], SortedSet(tmp))
        self.assertEqual(ss.by_score[1.5:3.1], SortedSet(tmp))
        tmp = data.copy()
        del tmp['three']
        self.assertEqual(ss.by_score[0.5:3], SortedSet(tmp))
        self.assertEqual(ss.by_score[0.5:2.5], SortedSet(tmp))
        self.assertEqual(ss.by_score[:2.5], SortedSet(tmp))
        self.assertEqual(ss.by_score[:3], SortedSet(tmp))
        self.assertEqual(ss.by_score[:2.01], SortedSet(tmp))
        del tmp['one']
        self.assertEqual(ss.by_score[1.01:2.01], SortedSet(tmp))
        self.assertEqual(ss.by_score[1.99:2.01], SortedSet(tmp))
        self.assertEqual(ss.by_score[2:2.01], SortedSet(tmp))
        self.assertEqual(ss.by_score[2:2.99], SortedSet(tmp))
        self.assertEqual(ss.by_score[2.01:2.99], SortedSet())
        self.assertEqual(ss.by_score[:2], SortedSet({'one': 1}))
        self.assertEqual(ss.by_score[:1.01], SortedSet({'one': 1}))
        self.assertEqual(ss.by_score[:1.99], SortedSet({'one': 1}))
        self.assertEqual(ss.by_score[3:], SortedSet({'three': 3}))
        self.assertEqual(ss.by_score[2.01:], SortedSet({'three': 3}))
        self.assertEqual(ss.by_score[2.99:], SortedSet({'three': 3}))
        self.assertEqual(ss.by_score[3.01:], SortedSet())

        self.assertEqual(ss.by_score[
            fractions.Fraction(4/3):fractions.Fraction(7/3)
            ], SortedSet({'two1': 2, 'two2': 2, 'two3': 2}))

    def test_delete_all_cases(self):
        for levels in product(range(1, 4), range(1, 4), range(1, 4)):
            # delete middle
            ss = SortedSet()
            with patch.object(ss, '_random_level', side_effect=levels) as p:
                ss['one'] = 1
                ss['two'] = 2
                ss['three'] = 3
                del ss['two']
                self.assertEqual(ss['one'], 1)
                self.assertEqual(ss['three'], 3)
                with self.assertRaises(KeyError):
                    ss['two']
                self.assertEqual(list(ss), ['one', 'three'])
            # delete first
            ss = SortedSet()
            with patch.object(ss, '_random_level', side_effect=levels) as p:
                ss['one'] = 1
                ss['two'] = 2
                ss['three'] = 3
                del ss['one']
                self.assertEqual(ss['two'], 2)
                self.assertEqual(ss['three'], 3)
                with self.assertRaises(KeyError):
                    ss['one']
                self.assertEqual(list(ss), ['two', 'three'])
            # delete last
            ss = SortedSet()
            with patch.object(ss, '_random_level', side_effect=levels) as p:
                ss['one'] = 1
                ss['two'] = 2
                ss['three'] = 3
                del ss['three']
                self.assertEqual(ss['one'], 1)
                self.assertEqual(ss['two'], 2)
                with self.assertRaises(KeyError):
                    ss['three']
                self.assertEqual(list(ss), ['one', 'two'])


class TestFuzzy(unittest.TestCase):

    def test_insert_integers(self):
        items = [  # fifty random values
             ('Xe2W0QxllGdCW251l7U9Dg', 150),
             ('3HT/SVSdCwM+4ZjtSqHCew', 476),
             ('Q2BKuEOFwIojkPsnjmPNFg', 2390),
             ('Qjq1fGnHVc5nXvWnbEyXjQ', 3773),
             ('wamjIdfm+ajk81fR7gKcAA', 4729),
             ('uDUHFv5CtiY/Gm5LOCfGUg', 6143),
             ('78l934GXETN68sql2vjP5w', 6487),
             ('1LAwgvIO0tEikYySkaSaXw', 7449),
             ('Y4mDqz7LfIV4L8h2aUwAkA', 10234),
             ('AidPceym19y/lmIdi6JxQQ', 10779),
             ('hHqwNSMusq7O895yFkr+rQ', 10789),
             ('dg16QiUDC2rgE39FWTSOxg', 11873),
             ('sgAdgtQ5wRFGSOZ3xZYHyA', 12273),
             ('OACKY0A1ftBbyLvTzyf8lQ', 12776),
             ('f+dLA1jK8EFEAHxm1FKUkA', 13079),
             ('1uDN4mSmsEQF/o6VNiBl3g', 13147),
             ('nNwOvGfk9AH2tIzK8uNdzQ', 16636),
             ('tMUZ6A1e/1SKd3ko0FhhBQ', 17933),
             ('M77ZQiFlYeU4ySUtVa6XYg', 18570),
             ('fY7RKQu8toBxoug4CMmznA', 18711),
             ('UaZorA+/GnCL4nmgLs3c/g', 19968),
             ('VbXaOsRHqH2CAoNJiYsrqg', 20064),
             ('dAr84/axpItIAjjNcVPzHA', 20250),
             ('HjzS0QlpofFhDO2iU4mXAw', 20756),
             ('ipksmQaeYErYwjZ6ia46TA', 21084),
             ('XemDsutAYPpCZ6WY4M//ig', 21609),
             ('6U6fbOs8jYVfqWeArQ5HHQ', 22410),
             ('QFblGefWYZqFbuSK0SDPRQ', 23267),
             ('J13bR75czCiLfeBcIy4XTg', 26556),
             ('e6XlDT9h6GVPdfvBOrXW5Q', 26608),
             ('/eLYo+GKgAt7I2PrOrFTzQ', 28597),
             ('48W/xF+VIQZoyKlhktifMw', 31364),
             ('NTUtbi4YOHiNIV6SVrpwyg', 33709),
             ('364+KUYYuwlmezv1EvaE0g', 33945),
             ('YaD6Ktqw1iIWcFGgMEvMxg', 38248),
             ('cJSZfsidFuaMK9jY15g44A', 38668),
             ('UeP/HvscsnQXUK37Dyo8/w', 40861),
             ('xon2bN9ZToI4LpN4o7M2nQ', 41836),
             ('MQKXJCNNtWsRqoGbSaDorw', 47171),
             ('LCcqUwfmOFq+VXI2kGBQow', 49311),
             ('gMXF4DMHCWBjbgucOqWKQg', 50725),
             ('JKHDvGMcLQrR4G3zC2g9ug', 50875),
             ('Mp1feZZmnmMPJk8bGv0NaA', 51017),
             ('rhZyspOoakQBO9Ses3jl+A', 53781),
             ('JB9bMHKHoT+hMVjuBrbqlg', 56409),
             ('/DsgGH+7F6Fh2/81SzyXYA', 56512),
             ('InjjAuUMGHYUIRdRnkUw2w', 56903),
             ('otVFi6DLAO+v7XUAcmKttA', 57114),
             ('mVTvHObgjfzvZLOzl/xo2Q', 58550),
             ('uU1yLoXCgPtifROhCST0sA', 60267)]
        keys = list(map(itemgetter(0), items))
        values = list(map(itemgetter(1), items))

        # simple checks
        set_n = SortedSet(items)
        set_r = SortedSet(reversed(items))
        for cur in (set_n, set_r):
            self.assertEqual(list(cur), keys)
            self.assertEqual(list(cur.keys()), keys)
            self.assertEqual(list(cur.values()), values)
            self.assertEqual(list(cur.items()), items)
        for idx in range(len(items)):
            key, score = items[idx]
            self.assertEqual(set_n.index(key), idx)
            self.assertEqual(set_r.index(key), idx)
            self.assertEqual(set_n.by_index[idx], key)
            self.assertEqual(set_r.by_index[idx], key)

        # slicing for various combinations
        ends = (None, 0, 2, 5, 10, 49, 50, 51, -1, -2, -5, -10, -49, 50, -51)
        steps = (None, 1, 2, 3)
        for start, stop, step in product(ends, ends, steps):
            self.assertEqual(list(set_n.by_index[start:stop:step].items()),
                             items[start:stop:step])
            self.assertEqual(list(set_r.by_index[start:stop:step].items()),
                             items[start:stop:step])

        # Lets test 7 random insertion orders
        for i in (10, 20, 30, 40, 50, 60, 70):
            rnd = random.Random(i)
            to_insert = copy.copy(items)
            rnd.shuffle(to_insert)

            # Let's check several sets created with different methods
            set1 = SortedSet()
            for k, v in to_insert:
                set1[k] = v
            set2 = SortedSet(to_insert)
            set3 = SortedSet(set1)
            set4 = SortedSet(set2)

            # Check all of them
            cursets = (set1, set2, set3, set4)
            for cur in cursets:
                self.assertEqual(list(cur), keys)
                self.assertEqual(list(cur.keys()), keys)
                self.assertEqual(list(cur.values()), values)
                self.assertEqual(list(cur.items()), items)

            # Check equality of all combinations
            all_sets = (set_n, set_r, set1, set2, set3, set4)
            for s1, s2 in combinations(all_sets, 2):
                self.assertEqual(s1, s2)

            # Let's pick up items to delete
            left = copy.copy(items)
            to_delete = []
            for i in range(rnd.randrange(10, 30)):
                idx = random.randrange(len(left))
                to_delete.append(left[idx])
                del left[idx]

            # Let's test deletion
            for cur in cursets:
                rnd.shuffle(to_delete)
                for key, value in to_delete:
                    del cur[key]
                self.assertEqual(list(cur.items()), left)
                self.assertNotEqual(cur, set_n)
                self.assertNotEqual(cur, set_r)

            # Let's reinsert keys in random order, and check if it's still ok
            for cur in cursets:
                rnd.shuffle(to_delete)
                for key, value in to_delete:
                    cur[key] = value
                self.assertEqual(cur, set_n)
                self.assertEqual(cur, set_r)
                self.assertEqual(list(cur.items()), items)
                for idx in range(len(items)):
                    key, score = items[idx]
                    self.assertEqual(cur.index(key), idx)
                    self.assertEqual(cur.by_index[idx], key)


if __name__ == '__main__':
    unittest.main()
