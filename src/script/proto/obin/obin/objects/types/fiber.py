from root import W_Root, W_Callable
from obin.runtime.error import *
from obin.objects import api
from rpython.rlib import jit


class W_Fiber(W_Callable):
    def __init__(self, fiber):
        self.fiber = fiber

    def _tostring_(self):
        return "fn fiber.yield {[native code]}"

    def _tobool_(self):
        return True

    def _call_(self, process, args):
        from obin.objects.space import newundefined

        if not self.fiber.is_waiting():
            raise ObinRuntimeError(u"Can't resume not waiting fiber")

        if api.n_length(args) == 0:
            value = newundefined()
        elif api.n_length(args) == 1:
            value = api.at_index(args, 0)
        else:
            value = args
        process.switch_to_fiber(self.fiber, value)


def newfiber(process):
    fiber1 = process.fiber
    w_fiber1 = W_Fiber(fiber1)
    fiber2 = process.create_fiber()
    w_fiber2 = W_Fiber(fiber2)
    return w_fiber1, w_fiber2


def activate_fiber(process, fiber_wrap, function, args):
    process.activate_fiber(fiber_wrap.fiber, function, args)
