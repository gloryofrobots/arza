__author__ = 'gloryofrobots'
import unittest
import test_pmap
def run():
    import sys
    sys.argv = sys.argv[0:1]
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(test_pmap.TestPMap)
    unittest.TextTestRunner(verbosity=2).run(suite)
