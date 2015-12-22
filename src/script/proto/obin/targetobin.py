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
    finally:
        return 0

def run(script_file):
    from obin.runtime.interpret import load_file, run_src
    from obin.utils import fs
    from obin.objects.space import newprocess
    script_dir = fs.dirname(script_file)

    path = unicode(fs.join_and_normalise_path(script_dir, "olib"))

    process = newprocess([path])
    src = load_file(script_file)
    print run_src(process, src)

# _____ Define and setup target ___
def target(driver, args):
    driver.exe_name = 'obin-script'
    return entry_point, None

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def entry_point(argv):
    return main(argv)

