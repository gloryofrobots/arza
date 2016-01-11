__author__ = 'gloryofrobots'
from rpython.rlib import jit
from obin.objects.space import newundefined
from obin.objects.types import plist
# TODO proper stack operations

class Stack:
    def __init__(self, size):
        self.data = None
        self.__pointer = 0
        self.data = [newundefined()] * size

    def pointer(self):
        return jit.promote(self.__pointer)

    def pop(self):
        e = self.top()
        i = self.pointer() - 1
        assert i >= 0
        self.data[i] = newundefined()
        self.set_pointer(i)
        return e

    def top(self):
        i = self.pointer() - 1
        if i < 0:
            raise IndexError
        return self.data[i]

    def grow(self, size):
        assert size > 0
        l = self.size()
        if size <= l:
            return

        self.data = self.data + [newundefined()] * (size - l)

    def size(self):
        return len(self.data)

    def push(self, element):
        from obin.objects.space import isnull, isany
        if not isany(element):
            raise RuntimeError(u"Not Any product", element)
        i = self.pointer()
        size = self.size()
        assert i >= 0
        if i >= size:
            self.grow(size + 32)

        self.data[i] = element
        self.set_pointer(i + 1)

    def set_pointer(self, p):
        self.__pointer = p

    @jit.unroll_safe
    def pop_n(self, n):
        if n < 1:
            return []

        result = []
        i = n
        while i > 0:
            i -= 1
            e = self.pop()
            result = [e] + result

        return result

    @jit.unroll_safe
    def pop_n_list(self, n):
        lst = plist.empty()
        if n < 1:
            return lst

        i = n
        while i > 0:
            i -= 1
            value = self.pop()
            lst = plist.prepend(value, lst)

        return lst
