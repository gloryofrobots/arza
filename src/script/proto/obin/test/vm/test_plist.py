from obin.types import plist, space, api
from obin.runtime.error import ObinError
import unittest


def make_test_data(vals):
    return [space.newint(val) for val in vals]


def inc(el):
    from obin.types import api, space
    return space.newint(api.to_i(el) + 1)


class PListTestCase(unittest.TestCase):
    def _test_equal(self, pl, check):
        check = make_test_data(check)
        self.assertEqual(plist.length(pl), len(check))
        for li, ci in zip(pl, check):
            self.assertTrue(api.n_equal(li, ci))
            # print "TEST FAILED ", pl, check

    def test_plist(self):
        NI = space.newint
        NIS = lambda items: [NI(i) for i in items]

        l = plist.plist(NIS([0]))
        l1 = plist.prepend(NI(1), l)
        l2 = plist.prepend(NI(2), l1)
        l3 = plist.prepend(NI(3), l2, )
        self._test_equal(l3, [3, 2, 1, 0])
        l4 = plist.insert(l3, 1, NI(44))
        self._test_equal(l4, [3, 44, 2, 1, 0])

        l5 = plist.insert(l4, 2, NI(55))
        self._test_equal(l5, [3, 44, 55, 2, 1, 0])
        l6 = plist.take(l5, 3)
        self._test_equal(l6, [3, 44, 55])

        l7 = plist.remove(l6, NI(44))
        self._test_equal(l7, [3, 55])
        l7_1 = plist.remove(l6, NI(55))
        self._test_equal(l7_1, [3, 44])

        l8 = plist.cons_n_list(NIS([123, 124, 125, 123, 124, 125]), l7)
        self._test_equal(l8, [123, 124, 125, 123, 124, 125, 3, 55])
        l8_1 = plist.remove_all(l8, NI(125))
        self._test_equal(l8_1, [123, 124, 123, 124, 3, 55])

        l9 = plist.reverse(l8)
        self._test_equal(l9, list(reversed([123, 124, 125, 123, 124, 125, 3, 55])))

        l10 = plist.concat(l8, l9)
        self._test_equal(l10, [123, 124, 125, 123, 124, 125, 3, 55, 55, 3, 125, 124, 123, 125, 124, 123])

        l11 = plist.fmap(inc, l10)
        self._test_equal(l11, [124, 125, 126, 124, 125, 126, 4, 56, 56, 4, 126, 125, 124, 126, 125, 124])

        l12 = plist.plist(NIS([1, 2, 3]))
        l13 = plist.plist(NIS([1, 2, 3, 4, 5]))
        l14 = plist.substract(l13, l12)
        self._test_equal(l14, [4, 5])

        l15 = plist.plist(NIS([1, 2, 3, 4, 5, 6, 7, 8]))

        l16 = plist.slice(l15, 0, 3)
        self._test_equal(l16, [1, 2, 3])

        l17 = plist.slice(l15, 1, 6)
        self._test_equal(l17, [2, 3, 4, 5, 6])

        l18 = plist.update(l17, 0, NI(102))
        self._test_equal(l18, [102, 3, 4, 5, 6])
        l19 = plist.update(l18, 3, NI(105))
        self._test_equal(l19, [102, 3, 4, 105, 6])
        l20 = plist.update(l19, 4, NI(106))
        self._test_equal(l20, [102, 3, 4, 105, 106])
        l21 = plist.plist(NIS([1, 2, 3, 4]))
        l22 = plist.append(l21, NI(5))
        self._test_equal(l22, [1, 2, 3, 4, 5])

        l23 = plist.plist(NIS([3, 4, 5]))
        self.assertTrue(plist.contains_list(l22, l23))
        l24 = plist.plist(NIS([2, 4, 5]))
        self.assertFalse(plist.contains_list(l22, l24))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(PListTestCase)
    return suite
