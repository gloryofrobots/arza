#!/usr/bin/env python

import os

def printmessage(msg):
    assert isinstance(msg, unicode)
    from arza.misc.strutil import encode_unicode_utf8
    os.write(1, encode_unicode_utf8(msg))


def main(argv):
    from arza.misc import timer
    with timer.Timer("Lalan Main", True):

        script_file = argv[1]
        if script_file == "--test":
            from test.vm import tests
            return tests.run()

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
    from arza.runtime import engine
    from arza.misc import fs
    abs_script_path = fs.abspath(script_file)
    if not fs.is_file(abs_script_path):
        raise RuntimeError("Invalid script path " + abs_script_path)

    script_dir = fs.get_dirname(fs.abspath(script_file))
    path_lib = fs.join_and_normalise_path(script_dir, "__std__")

    if not fs.is_directory(path_lib):
        raise RuntimeError("Invalid __std__ dir path " + path_lib)

    process, error = engine.initialize([script_dir, path_lib])
    if error is not None:
        return error
    return engine.evaluate_file(process, script_file)

# # _____ Define and setup target ___
def target(driver, args):
    driver.exe_name = 'lalan_i'
    return entry_point, None


def jitpolicy(driver):
    from arza.misc.platform import JitPolicy
    return JitPolicy()


def entry_point(argv):
    return main(argv)


# class writer(object):
#     def write(self, data):
#         pass
#
#     def isatty(self):
#         return False

if __name__ == '__main__':
    import sys
    # sys.stderr = writer()
    entry_point(sys.argv)
