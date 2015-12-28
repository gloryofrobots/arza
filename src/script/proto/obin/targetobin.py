#!/usr/bin/env python

import os
from rpython.rlib.objectmodel import enforceargs

@enforceargs(unicode)
def printmessage(msg):
    from obin.runistr import encode_unicode_utf8
    os.write(1, encode_unicode_utf8(msg))

def main(argv):
    script_file = argv[1]
    result = run(script_file)
    print ">>>", result
    # try:
    #     run(script_file)
    # except SystemExit:
    #     printmessage(u"Exit")
    #     return 1
    # except Exception as e:
    #     print "Exception", e
    #     raise
    # finally:
    #     return 0

def run(script_file):
    from obin.runtime import engine
    from obin.utils import fs
    script_dir = fs.get_dirname(script_file)
    path = fs.join_and_normalise_path(script_dir, "olib")

    process = engine.initialize([path])
    return engine.evaluate_file(process, script_file)

# _____ Define and setup target ___
def target(driver, args):
    driver.exe_name = 'obin_i'
    return entry_point, None

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def entry_point(argv):
    return main(argv)

if __name__ == '__main__':
    import sys
    entry_point(sys.argv)

