from root import W_Callable
from obin.runtime import error
from obin.types import api, space, tuples


class W_Fiber(W_Callable):
    def __init__(self, fiber):
        self.fiber = fiber

    def _to_string_(self):
        return "<fiber>"

    def _type_(self, process):
        return process.std.types.Fiber

    def _call_(self, process, args):
        if not self.fiber.is_waiting():
            error.throw_1(error.Errors.FIBER_FLOW_ERROR, space.newstring(u"Can't resume active fiber"))

        if api.length_i(args) == 0:
            value = space.newunit()
        elif api.length_i(args) == 1:
            value = api.at_index(args, 0)
        else:
            value = args
        process.switch_to_fiber(self.fiber, value)

    def _equal_(self, other):
        return self is other

"""
import tvar
import from _fiber (spawn, activate, coroutine)
fun coroutine fn ->
    (fiber1, fiber2) = spawn ()

    first_call = tvar:create False

    fun _coroutine_handler ...args ->

        if (tvar:read first_call) `is` False ->
            tvar:swap first_call True
            activate fiber2 .
                     lam () -> apply fn (concat (fiber1, ) . args) end
        else ->
            apply fiber2 args
"""
class W_Coroutine(W_Callable):
    def __init__(self, fn, fiber1, fiber2):
        self.initialised = False
        self.fiber1 = fiber1
        self.fiber2 = fiber2
        self.fn = fn

    def _call_(self, process, args):
        if not self.initialised:
            new_args = tuples.concat(space.newtuple([self.fiber1]), args)
            process.activate_fiber(self.fiber2.fiber, self.fn, new_args)
            self.initialised = True
        else:
            api.call(process, self.fiber2, args)

    def _equal_(self, other):
        return self is other

    def _to_string_(self):
        return self.fn._to_string_()

    def _type_(self, process):
        return process.std.types.Function


def newfiber(process):
    fiber1 = process.fiber
    w_fiber1 = W_Fiber(fiber1)
    fiber2 = process.create_fiber()
    w_fiber2 = W_Fiber(fiber2)
    return w_fiber1, w_fiber2


def activate_fiber(process, fiber_wrap, function, args):
    process.activate_fiber(fiber_wrap.fiber, function, args)

def newcoroutine(process, fn):
    fiber1, fiber2 = newfiber(process)
    return W_Coroutine(fn, fiber1, fiber2)