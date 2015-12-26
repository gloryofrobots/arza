#!/usr/bin/env python

import os
from rpython.rlib.objectmodel import enforceargs

@enforceargs(unicode)
def printmessage(msg):
    from obin.runistr import encode_unicode_utf8
    os.write(1, encode_unicode_utf8(msg))

def main(argv):
    script_file = argv[1]
    try:
        run(script_file)
    except SystemExit:
        printmessage(u"Exit")
        return 1
    except Exception as e:
        print "Exception", e
    finally:
        return 0

def run(script_file):
    # print "RUN", script_file
    from obin.runtime.interpret import load_file, evaluate
    from obin.utils import fs
    from obin.objects.space import newprocess
    script_dir = fs.dirname(script_file)

    path = fs.join_and_normalise_path(script_dir, "olib")
    # print "RUN PATH", path

    process = newprocess([path])

    # print "RUN process", process
    src = load_file(script_file)
    print evaluate(process, src)

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

