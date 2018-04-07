from arza.types.root import W_Hashable
from arza.types import api, space, plist, tuples
from arza.misc import platform
from arza.types import api, space, plist, symbol
from arza.types.root import W_Root, W_Callable
from arza.misc.platform import is_absent_index
from arza.runtime import error


class W_Instance(W_Hashable):
    def __init__(self, cls, slots):
        W_Hashable.__init__(self)
        # list of all known interfaces
        self.cls = cls
        self.slots = slots

    def _at_(self, key):
        val = api.lookup(self.slots, key, space.newvoid())
        if space.isvoid(val):
            return self.cls.lookup_symbol(key)
        return val

    def set_class(self, cls):
        self.cls = cls

    def _put_(self, k, v):
        self.slots._put_(k, v)
        return self

    def _compute_hash_(self):
        return int((1 - platform.random()) * 10000000)

    def _equal_(self, other):
        return other is self

    def _type_(self, process):
        return self.cls

    def _to_string_(self):
        return "<instance %s %s>" % (api.to_s(self.cls), api.to_s(self.slots))

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
        from arza.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_result, None, self.ctor, args)
        return routine


class W_Class(W_Instance):
    def __init__(self, name, base, metaclass, slots, env):
        W_Instance.__init__(self, metaclass, slots)
        self.name = name
        self.slots = slots
        self.base = base
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
            cls = cls.base
            if space.isnil(cls):
                break
        return space.newvoid()

    def _call_(self, process, args):
        obj = W_Instance(self, space.new_empty_assoc_array())
        ctor = self.lookup_symbol(process.symbols.init)
        if space.isvoid(ctor):
            return obj
        else:
            new_args = tuples.prepend(args, obj)
            process.call_object(W_Constructor(ctor, obj), new_args)

    def _equal_(self, other):
        return other is self

    def _to_string_(self):
        return "<class %s>" % (api.to_s(self.name))

    def _to_repr_(self):
        return self._to_string_()


def newcompiledclass(name, base, metaclass, env):
    if space.isnil(name):
        name = env.name
    slots = env.data
    return W_Class(name, base, metaclass, slots, env)


def newclass(name, base, metaclass, slots):
    return W_Class(name, base, metaclass, slots, None)
