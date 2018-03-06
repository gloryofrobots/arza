__author__ = 'gloryofrobots'
from arza.types import pmap, space, api
from arza.runtime.error import ArzaError
import unittest

class PMapTestCase(unittest.TestCase):
    def test_pmap(self):
        S = space.newstring
        undef = space.newvoid()
        m = pmap.pmap([S(u"age"),S(u"42")])
        self.assertEqual(api.at(m, S(u"age")), S(u"42"))
        m1 = api.put(m, S(u"name"), S(u"Bob"))
        self.assertEqual(api.length_i(m1), 2)
        self.assertEqual(api.at(m1, S(u"name")), S(u"Bob"))

        m2 = api.put(m1, S(u"surname"), S(u"Alice"))
        self.assertEqual(api.length_i(m2), 3)
        self.assertEqual(api.at(m2, S(u"surname")), S(u"Alice"))
        self.assertEqual(api.lookup(m2, S(u"age"), undef), S(u"42"))
        self.assertNotEqual(api.lookup(m2, S(u"age"), undef), S(u"43"))
        self.assertRaises(ArzaError, api.at, m2, S(u"surname1"))

def suite():
    # tests = ['test_pmap']
    # suite = unittest.TestSuite()
    # suite.addTests(map(PMapTestCase, tests))
    suite = unittest.TestLoader().loadTestsFromTestCase(PMapTestCase)
    return suite
