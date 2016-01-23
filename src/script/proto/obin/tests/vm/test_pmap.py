__author__ = 'gloryofrobots'
from obin.types import pmap, space, api
from obin.runtime.error import ObinError
import unittest

class TestPMap(unittest.TestCase):
    def test_pmap(self):
        S = space.newstring
        undef = space.newundefined()
        m = pmap.pmap([S(u"age"),S(u"42")])
        self.assertEqual(api.at(m, S(u"age")), S(u"42"))
        m1 = api.put(m, S(u"name"), S(u"Bob"))
        self.assertEqual(api.n_length(m1), 2)
        self.assertEqual(api.at(m1, S(u"name")), S(u"Bob"))

        m2 = api.put(m1, S(u"surname"), S(u"Alice"))
        self.assertEqual(api.n_length(m2), 3)
        self.assertEqual(api.at(m2, S(u"surname")), S(u"Alice"))
        self.assertEqual(api.lookup(m2, S(u"age"), undef), S(u"42"))
        self.assertNotEqual(api.lookup(m2, S(u"age"), undef), S(u"43"))
        self.assertRaises(ObinError, api.at, m2, S(u"surname1"))

