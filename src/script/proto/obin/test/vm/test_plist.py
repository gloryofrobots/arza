from obin.types import plist, space, api
from obin.runtime.error import ObinError
import unittest


def make_test_data(vals):
    return [space.newint(val) for val in vals]


def inc(el):
    from obin.types import api, space
    return space.newint(api.to_native_integer(el) + 1)


class PListTestCase(unittest.TestCase):
    def _test_equal(self, pl, check):
        check = make_test_data(check)
        assert plist.length(pl) == len(check)
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
        # print remove_all(l8, ni(125))
        l9 = plist.reverse(l8)
        # print l9
        l10 = plist.concat(l8, l9)
        # print l10

        l11 = plist.fmap(inc, l10)
        # print l11
        l12 = plist.plist(NIS([1, 2, 3]))
        l13 = plist.plist(NIS([1, 2, 3, 4, 5]))
        l14 = plist.substract(l13, l12)
        self._test_equal(l14, [4, 5])
        # l9 = newlist(nis([1,2,2,3,4,5,2,6,2,7]))
        # l9 = newlist(nis([1,2,3]))
        # print l9
        # l10 = remove_all(l9, ni(2))
        # print l10


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(PListTestCase)
    return suite
