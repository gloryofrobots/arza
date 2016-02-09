from rpython.rlib.objectmodel import (specialize, enforceargs,
                                      compute_unique_id, compute_identity_hash,
                                      always_inline)
from rpython.rlib.rrandom import Random
from rpython.rlib.rarithmetic import ovfcheck, intmask

r = Random()

NOT_FOUND = -1


def random():
    return r.random()


@always_inline
@enforceargs(int)
def is_absent_index(idx):
    return idx == NOT_FOUND


@always_inline
def absent_index():
    return NOT_FOUND


@specialize.argtype(0)
def obin_hash(obj):
    return compute_identity_hash(obj)


@specialize.argtype(0)
def obin_id(obj):
    return compute_unique_id(obj)


class Timer(object):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, *args):
        import time
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs


def get_line(string, line_no):
    index = -1
    for _ in range(line_no - 1):
        index = string.index('\n', index + 1)

    try:
        last_index = string.index('\n', index + 1)
        result = string[index + 1:last_index]
    except ValueError:
        result = string[index + 1:]

    result = result.lstrip()
    return unicode(result)


def get_line_for_position(string, pos):
    try:
        index = string.index('\n', pos + 1)
        result = string[pos: index]
    except:
        result = string[pos:]
    return unicode(result)


def is_quoted_string(string):
    if string.startswith('"') and string.endswith('"'):
        return True
    if string.startswith("'") and string.endswith("'"):
        return True
    return False


def string_unquote(string):
    s = string
    if s.startswith('"'):
        assert s.endswith('"')
    else:
        assert s.startswith("'")
        assert s.endswith("'")
    s = s[:-1]
    s = s[1:]

    return s
