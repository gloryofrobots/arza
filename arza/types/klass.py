from arza.types.root import W_Hashable
from arza.types import api, space, plist, tuples
from arza.misc import platform
from arza.runtime import error

class W_Object(W_Hashable):
    def __init__(self, parent, slots):
        W_Hashable.__init__(self)
        # list of all known interfaces
        self.parent = parent
        self.slots = slots

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _type_(self, process):
        return process.std.types.Datatype

    def _to_string_(self):
        return "<Object>"

    def _to_repr_(self):
        return self._to_string_()


class W_Klass(W_Hashable):
    def __init__(self, name, base, static_vars, funcs, slots, methods):
        W_Hashable.__init__(self)
        # list of all known interfaces
        self.name = name
        self.base = base
        self.static_vars = static_vars
        self.funcs = funcs
        self.slots = slots
        self.methods = methods

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _type_(self, process):
        return process.std.types.Datatype

    def _to_string_(self):
        return "<datatype %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()

