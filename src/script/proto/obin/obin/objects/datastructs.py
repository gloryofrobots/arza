__author__ = 'gloryofrobots'
from rpython.rlib import jit, debug
from rpython.rlib.objectmodel import enforceargs
from obin.objects.object_space  import newundefined


# @jit.elidable
# def sign(i):
#     if i > 0:
#         return 1
#     if i < 0:
#         return -1
#     return 0

# MASK_32 = (2 ** 32) - 1
# MASK_16 = (2 ** 16) - 1
#
# @enforceargs(int)
# @jit.elidable
# def int32(n):
#     if n & (1 << (32 - 1)):
#         res = n | ~MASK_32
#     else:
#         res = n & MASK_32
#
#     return res
#
#
# @enforceargs(int)
# @jit.elidable
# def uint32(n):
#     return n & MASK_32
#
#
# @enforceargs(int)
# @jit.elidable
# def uint16(n):
#     return n & MASK_16



class Slots(object):
    def __init__(self, size=0):
        if size:
            self._property_slots_ = [None] * size
        else:
            self._property_slots_ = []

        self._size = size
        self._property_map_ = {}
        self._index = 0


    def to_dict(self):
        m = {}
        for n, v in self._property_map_.items():
            m[n] = self._property_slots_[v]

        return m

    def __str__(self):
        return str(self.to_dict())
        pass

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        from copy import copy
        clone = Slots(0)
        clone._property_slots_ = copy(self._property_slots_)
        clone._property_map_ = copy(self._property_map_)
        clone._index = self._index
        return clone

    def contains(self, name):
        return name in self._property_map_

    def values(self):
        return self._property_slots_

    def length(self):
        return len(self._property_slots_)

    def keys(self):
        return self._property_map_.keys()

    def get_by_index(self, index):
        return self._property_slots_[index]

    def get(self, name):
        idx = self.get_index(name)
        if idx is None:
            return

        return self.get_by_index(idx)

    def delete(self, name):
        idx = self.get_index(name)
        if idx is None:
            return

        assert idx >= 0
        self._property_slots_ = self._property_slots_[:idx] + self._property_slots_[idx + 1:]
        del self._property_map_[name]

    def get_index(self, name):
        try:
            idx = self._property_map_[name]
        except KeyError:
            return None
        return idx

    def add(self, name, value):
        idx = self.get_index(name)
        if idx is None:
            idx = self._index
            self._property_map_[name] = idx
            self._index += 1

        if idx >= len(self._property_slots_):
            self._property_slots_ = self._property_slots_ + ([None] * (1 + idx - len(self._property_slots_)))

        self._property_slots_[idx] = value
        return idx

    def set(self, name, value):
        idx = self.get_index(name)
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

    def __iter__(self):
        return self.__data.__iter__()

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
