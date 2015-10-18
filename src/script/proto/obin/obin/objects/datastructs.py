__author__ = 'gloryofrobots'
from rpython.rlib import jit, debug
from rpython.rlib.objectmodel import enforceargs
from obin.objects.object_space  import newundefined

@jit.elidable
def is_array_index(p):
    return make_array_index(p) != NOT_ARRAY_INDEX

NOT_ARRAY_INDEX = -1

class Descr(object):
    def __init__(self, can_put, own, inherited, prop):
        self.can_put = can_put
        self.own = own
        self.inherited = inherited
        self.prop = prop


@jit.unroll_safe
def make_array_index(idx):
    if len(idx) == 0:
        return -1

    IDX_LIT = '0123456789'

    for c in idx:
        if c not in IDX_LIT:
            return NOT_ARRAY_INDEX
    return int(idx)


@jit.elidable
def sign(i):
    if i > 0:
        return 1
    if i < 0:
        return -1
    return 0

MASK_32 = (2 ** 32) - 1
MASK_16 = (2 ** 16) - 1

@enforceargs(int)
@jit.elidable
def int32(n):
    if n & (1 << (32 - 1)):
        res = n | ~MASK_32
    else:
        res = n & MASK_32

    return res


@enforceargs(int)
@jit.elidable
def uint32(n):
    return n & MASK_32


@enforceargs(int)
@jit.elidable
def uint16(n):
    return n & MASK_16


class Map(object):
    NOT_FOUND = -1
    _immutable_fields_ = ['index', 'back', 'name']

    def __init__(self):
        self.index = self.NOT_FOUND
        self.forward_pointers = {}
        self.back = None
        self.name = None

    def __repr__(self):
        return "%(id)s %(back)s, [%(index)d]:%(name)s" % \
               {'id': str(hex(id(self))), 'back': repr(self.back), 'index': self.index, 'name': self.name}


    @jit.elidable_promote("0")
    def contains(self, name):
        idx = self.lookup(name)
        return self.not_found(idx) is False

    @jit.elidable_promote("0")
    def not_found(self, idx):
        return idx == self.NOT_FOUND

    @jit.elidable_promote("0")
    def lookup(self, name):
        node = self._find_node_with_name(name)
        if node is not None:
            return node.index
        return self.NOT_FOUND

    def _find_node_with_name(self, name):
        if self.name == name:
            return self
        if self.back is not None:
            return self.back._find_node_with_name(name)

    def _key(self):
        return (self.name)

    def empty(self):
        return True

    @jit.elidable
    def len(self):
        return self.index + 1

    @jit.elidable
    def add(self, name):
        assert self.lookup(name) == self.NOT_FOUND
        node = self.forward_pointers.get((name), None)
        if node is None:
            node = MapNode(self, name)
            self.forward_pointers[node._key()] = node
        return node

    @jit.elidable
    def keys(self):
        if self.name is None:
            return []

        k = [self.name]
        if self.back is not None:
            return self.back.keys() + k

        return k

    def delete(self, key):
        return self


class MapRoot(Map):
    def __repr__(self):
        return "Root:[%(index)d]:%(name)s" % {'index': self.index, 'name': self.name}


class MapNode(Map):
    def __init__(self, back, name):
        Map.__init__(self)
        self.back = back
        self.name = name
        self.index = back.index + 1

    @jit.elidable
    def delete(self, name):
        if self.name == name:
            return self.back
        else:
            n = self.back.delete(name)
            return n.add(self.name)

    def empty(self):
        return False


ROOT_MAP = MapRoot()


def new_map():
    return ROOT_MAP


class Slots(object):
    def __init__(self, size=0):
        if size:
            self._property_slots_ = [None] * size
        self._property_map_ = new_map()
        self._property_slots_ = []


    def contains(self, name):
        return self._property_map_.contains(name)

    def keys(self):
        return self._property_map_.keys()

    def get(self, name):
        idx = self._property_map_.lookup(name)

        if self._property_map_.not_found(idx):
            return

        prop = self._property_slots_[idx]
        return prop

    def delete(self, name):
        idx = self._property_map_.lookup(name)

        if self._property_map_.not_found(idx):
            return

        assert idx >= 0
        self._property_slots_ = self._property_slots_[:idx] + self._property_slots_[idx + 1:]
        self._property_map_ = self._property_map_.delete(name)

    def add(self, name, value):
        idx = self._property_map_.lookup(name)

        if self._property_map_.not_found(idx):
            self._property_map_ = self._property_map_.add(name)
            idx = self._property_map_.index

        if idx >= len(self._property_slots_):
            self._property_slots_ = self._property_slots_ + ([None] * (1 + idx - len(self._property_slots_)))

        self._property_slots_[idx] = value

    def set(self, name, value):
        idx = self._property_map_.lookup(name)
        self._property_slots_[idx] = value

def newslots():
    return Slots()

class Table(object):
    def __init__(self, data=None):
        if not data:
            self.data = {}
        else:
            assert(isinstance(data, dict))
            self.data = data

    def get(self, item):
        return self.data.get(item, newundefined())

    def set(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return str(self.data)


class Stack(object):
    def __init__(self, size=1):
        self.__data = None
        self.__pointer = None
        self.init(size)

    def init(self, size=1):
        self.__data = [None] * size
        self.__pointer = 0

    def pointer(self):
        return jit.promote(self.__pointer)

    def pop(self):
        e = self.top()
        i = self.pointer() - 1
        assert i >= 0
        self.__data[i] = None
        self.set_pointer(i)
        return e

    def top(self):
        i = self.pointer() - 1
        if i < 0:
            raise IndexError
        return self.__data[i]

    def size(self):
        return len(self.__data)

    def push(self, element):
        # from obin.utils import tb
        # if str(element) == "undefined":
        #     tb("CHECK!!!!!!!!!!")
        #     print "UNDEFINED IS SET ", hex(id(self.routine()))
        i = self.pointer()
        len_stack = len(self.__data)

        assert i >= 0 and len_stack > i

        self.__data[i] = element
        self.set_pointer(i + 1)

    def set_pointer(self, p):
        self.__pointer = p

    def pop_n(self, n):
        if n < 1:
            return []

        r = []
        i = n
        while i > 0:
            i -= 1
            e = self.pop()
            r = [e] + r

        return r
