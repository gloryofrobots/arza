__author__ = 'gloryofrobots'
from arza.misc.platform import jit
from arza.types import plist, space
from arza.runtime import error
# TODO proper stack operations

class Stack:
    def __init__(self, size):
        self.data = None
        self.__pointer = 0
        self.__pointer = jit.promote(self.__pointer)
        self.data = [space.newvoid()] * size

    def pointer(self):
        return self.__pointer

    def pop(self):
        e = self.top()
        i = self.pointer() - 1
        assert i >= 0
        self.data[i] = space.newvoid()
        self.set_pointer(i)
        return e

    def get(self, index):
        return self.data[index]

    def get_from_top(self, distance):
        return self.data[self.top_index() - distance]

    def top_index(self):
        return self.pointer() - 1

    def top(self):
        i = self.top_index()
        if i < 0:
            raise RuntimeError(i)
        return self.data[i]

    def grow(self, size):
        assert size > 0
        l = self.size()
        if size <= l:
            return

        self.data = self.data + [space.newvoid()] * (size - l)

    def size(self):
        return len(self.data)

    def swap(self):
        i = self.top_index()
        x = self.data[i]
        self.data[i] = self.data[i-1]
        self.data[i-1] = x

    def push(self, element):
        from arza.types.space import isany
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
        self.__pointer = jit.promote(self.__pointer)

    @jit.unroll_safe
    def pop_n_array(self, n):
        if n < 1:
            return space.newemptyarray()

        result = []
        i = n
        while i > 0:
            i -= 1
            e = self.pop()
            result = [e] + result

        return space.newarray(result)

