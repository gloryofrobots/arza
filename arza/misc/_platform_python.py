__author__ = 'gloryofrobots'
import re
import random as r
class rfloat:
    INFINITY = 1e200 * 1e200
    NAN = abs(INFINITY / INFINITY)
    @staticmethod
    def isnan(v):
        return v == rfloat.NAN
    @staticmethod
    def isinf(v):
        return v == rfloat.INFINITY

class rarithmetic:
    r_uint = long
    r_int = int

    @staticmethod
    def intmask(i):
        return i

    @staticmethod
    def ovfcheck(i):
        if not isinstance(i, int):
            raise OverflowError()
        return i

def decorator_args(*args, **kwargs):
    def wrap(f):
        def wrapped_f(*args):
            f(*args)

        return wrapped_f

    return wrap


def always_inline(f):
    def wrapped_f(*args):
        f(*args)

    return wrapped_f


class rstring:
    class UnicodeBuilder:
        def __init__(self, size=None):
            self.data = []

        def append(self, str):
            self.data.append(unicode(str))

        def build(self):
            return u"".join(self.data)


class runicode:
    @staticmethod
    def str_decode_utf_8(s, size, errors, final=False):
        return unicode(s), 0

    @staticmethod
    def unicode_encode_utf_8(string, _s, _d):
        return str(string)

    @staticmethod
    def str_decode_unicode_escape(s, size, errors, final=False):
        return unicode(s)


class jit:
    @staticmethod
    def promote(val):
        return val

    @staticmethod
    def elidable(f):
        def wrapped_f(*args):
            return f(*args)

        return wrapped_f

    @staticmethod
    def unroll_safe(f):
        def wrapped_f(*args):
            return f(*args)

        return wrapped_f


compute_unique_id = id
compute_identity_hash = hash

NOT_FOUND = -1


def random():
    return r.random()


def is_absent_index(idx):
    return idx == NOT_FOUND


def absent_index():
    return NOT_FOUND


JitPolicy = object()
lalan_hash = compute_identity_hash
lalan_id = compute_unique_id


class _r_dictkey(object):
    __slots__ = ['dic', 'key', 'hash']

    def __init__(self, dic, key):
        self.dic = dic
        self.key = key
        self.hash = dic.key_hash(key)

    def __eq__(self, other):
        if not isinstance(other, _r_dictkey):
            return NotImplemented
        return self.dic.key_eq(self.key, other.key)

    def __ne__(self, other):
        if not isinstance(other, _r_dictkey):
            return NotImplemented
        return not self.dic.key_eq(self.key, other.key)

    def __hash__(self):
        return self.hash

    def __repr__(self):
        return repr(self.key)


class r_dict(object):
    """An RPython dict-like object.
    Only provides the interface supported by RPython.
    The functions key_eq() and key_hash() are used by the key comparison
    algorithm."""

    def _newdict(self):
        return {}

    def __init__(self, key_eq, key_hash, force_non_null=False):
        self._dict = self._newdict()
        self.key_eq = key_eq
        self.key_hash = key_hash
        self.force_non_null = force_non_null

    def __getitem__(self, key):
        return self._dict[_r_dictkey(self, key)]

    def __setitem__(self, key, value):
        self._dict[_r_dictkey(self, key)] = value

    def __delitem__(self, key):
        del self._dict[_r_dictkey(self, key)]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        for dk in self._dict:
            yield dk.key

    def __contains__(self, key):
        return _r_dictkey(self, key) in self._dict

    def get(self, key, default):
        return self._dict.get(_r_dictkey(self, key), default)

    def setdefault(self, key, default):
        return self._dict.setdefault(_r_dictkey(self, key), default)

    def popitem(self):
        dk, value = self._dict.popitem()
        return dk.key, value

    def copy(self):
        result = self.__class__(self.key_eq, self.key_hash)
        result.update(self)
        return result

    def update(self, other):
        for key, value in other.items():
            self[key] = value

    def keys(self):
        return [dk.key for dk in self._dict]

    def values(self):
        return self._dict.values()

    def items(self):
        return [(dk.key, value) for dk, value in self._dict.items()]

    iterkeys = __iter__

    def itervalues(self):
        return self._dict.itervalues()

    def iteritems(self):
        for dk, value in self._dict.items():
            yield dk.key, value

    def clear(self):
        self._dict.clear()

    def __repr__(self):
        "Representation for debugging purposes."
        return 'r_dict(%r)' % (self._dict,)

    def __hash__(self):
        raise TypeError("cannot hash r_dict instances")
