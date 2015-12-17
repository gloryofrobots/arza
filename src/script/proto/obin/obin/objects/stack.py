__author__ = 'gloryofrobots'
from rpython.rlib import jit

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
        from obin.objects.space import isnull, isany
        assert isany(element)
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

    @jit.unroll_safe
    def pop_n_into(self, n, l):
        assert n > 0

        i = n
        while i > 0:
            i -= 1
            e = self.pop()
            l.append(e)

    @jit.unroll_safe
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

    @jit.unroll_safe
    def pop_n_to_tuple(self, n):
        assert n > 0

        r = (self.pop(), )
        i = n
        while i > 1:
            i -= 1
            e = self.pop()
            r = (e, ) + r

        return r
