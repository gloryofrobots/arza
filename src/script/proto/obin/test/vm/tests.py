__author__ = 'gloryofrobots'
import unittest
import test_pmap
import test_plist
def run():
    import sys
    sys.argv = sys.argv[0:1]
    # unittest.main()
    alltests = unittest.TestSuite([test_pmap.suite(),
                                   test_plist.suite()])
    unittest.TextTestRunner(verbosity=2).run(alltests)
