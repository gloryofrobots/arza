from capy.types.root import W_Hashable
from capy.types import api, space, plist, array
from capy.misc import platform
from capy.types import api, space, plist, symbol
from capy.types.root import W_Root, W_Callable
from capy.misc.platform import is_absent_index
from capy.runtime import error


class W_Object(W_Hashable):
    def __init__(self, _type, slots):
        W_Hashable.__init__(self)
        # list of all known interfaces
        self.super = _type
        self.slots = slots

    def _at_(self, key):
        val = api.lookup(self.slots, key, space.newvoid())
        if space.isvoid(val):
            return self.super.lookup_symbol(key)
        return val

    def resuper(self, cls):
        self.super = cls

    def _put_(self, k, v):
        self.slots._put_(k, v)
        return self

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _type_(self, process):
        return self.super

    def _to_string_(self):
        return "<instance %s %s>" % (api.to_s(self.super), api.to_s(self.slots))

    def _to_repr_(self):
        return self._to_string_()


class W_Constructor(W_Callable):
    def __init__(self, ctor, obj):
        self.ctor = ctor
        self.obj = obj

    def on_result(self, process, value):
        return self.obj

    def _to_routine_(self, stack, args):
        # print "TO ROUTINE"
        from capy.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_result, None, self.ctor, args)
        return routine


class W_Class(W_Object):
    def __init__(self, name, base, slots, env):
        W_Object.__init__(self, base, slots)
        self.name = name
        self.slots = slots
        self.env = env
        if env is not None:
            self.exports = env.exports()
        else:
            self.exports = space.newlist([])
        self.ctor = None

    def lookup_symbol(self, key):
        cls = self
        while True:
            val = api.lookup(cls.slots, key, space.newvoid())
            if not space.isvoid(val):
                return val
            cls = cls.super
            if space.isnil(cls):
                break
        return space.newvoid()

    def _type_(self, process):
        return process.std.classes.Class

    def _call_(self, process, args):
        obj = W_Object(self, space.newemptytable())
        ctor = self.lookup_symbol(process.symbols.init)
        if space.isvoid(ctor):
            return obj
        else:
            new_args = array.prepend(args, obj)
            process.call_object(W_Constructor(ctor, obj), new_args)

    def _equal_(self, other):
        return other is self

    def _to_string_(self):
        return "<class %s %s>" % (api.to_s(self.name), api.to_s(self.slots))

    def _to_repr_(self):
        return self._to_string_()


def newcompiledclass(name, base, env):
    if space.isnil(name):
        name = env.name
    slots = env.data
    return W_Class(name, base, slots, env)


def newclass(name, base, slots):
    return W_Class(name, base, slots, None)
