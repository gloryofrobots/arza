from arza.types.root import W_Hashable
from arza.types import api, space, plist, tuples
from arza.misc import platform
from arza.types import api, space, plist, symbol
from arza.types.root import W_Root, W_Callable
from arza.misc.platform import is_absent_index
from arza.runtime import error


class W_Object(W_Hashable):
    def __init__(self, cls, slots):
        W_Hashable.__init__(self)
        # list of all known interfaces
        self.cls = cls
        self.slots = slots

    def _at_(self, key):
        val = api.lookup(self.slots, key, space.newvoid())
        if space.isvoid(val):
            return self.cls._at_(key)

    def _put_(self, k, v):
        return self.slots._put_(k, v)

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _type_(self, process):
        return self.cls

    def _to_string_(self):
        return "<Object %s>" % api.to_s(self.slots)

    def _to_repr_(self):
        return self._to_string_()


class W_Class(W_Object):
    def __init__(self, metaclass, slots, name):
        W_Object.__init__(self, metaclass, slots)
        self.name = name
        self.slots = slots

    # def instance(self):
    #     obj = W_Object(self,

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _to_string_(self):
        return "<datatype %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()


def instance(process, _class):
    return W_Object(_class, space.newassocarray())


def new_compiled_class(metaclass, env):
    name = env.name
    slots = env.data()
    return W_Class(metaclass, slots, name)


def newclass(metaclass, slots, name):
    return W_Class(metaclass, slots, name)
