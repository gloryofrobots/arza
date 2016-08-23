from root import W_Callable
from lalan.runtime import error
from lalan.types import api, space, tuples


class W_FiberChannel(W_Callable):
    def __init__(self, fiber):
        self.fiber = fiber

    def _to_string_(self):
        return "<fiber channel>"

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.FiberChannel

    def _call_(self, process, args):
        if not self.fiber.is_passive():
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


class W_Coroutine(W_Callable):
    def __init__(self, fn, chan1, chan2):
        self.initialised = False
        self.chan1 = chan1
        self.chan2 = chan2
        self.fn = fn

    def on_result(self, process, value):
        return value

    def on_complete(self, process, value):
        # print "ON RESULT", value
        # yield to current owner
        if process.fiber != self.chan1.fiber:
            process.switch_to_fiber(self.chan1.fiber, value)
        return value

    #
    def _to_routine_(self, stack, args):
        # print "TO ROUTINE"
        from lalan.runtime.routine.routine import create_callback_routine
        routine = create_callback_routine(stack, self.on_complete, None, self.fn, args)
        return routine

    def _call_(self, process, args):
        self.chan1.fiber = process.fiber
        if not self.initialised:
            new_args = tuples.concat(space.newtuple([self.chan1]), args)
            process.activate_fiber(self.chan2.fiber, self, new_args)
            self.initialised = True
        else:
            api.call(process, self.chan2, args)

    def _equal_(self, other):
        return self is other

    def _to_string_(self):
        return "<coroutine of %s>" % self.fn._to_string_()

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.Coroutine

    def _is_empty_(self):
        return self.is_finished()

    def is_complete(self):
        return self.chan2.fiber.is_complete()

    def is_finished(self):
        return self.chan2.fiber.is_finished()

    def is_terminated(self):
        return not self.chan2.fiber.is_terminated()

    def is_active(self):
        return not self.chan2.fiber.is_active()

    def is_passive(self):
        return not self.chan2.fiber.is_passive()


def open_fiber_channel(process):
    fiber1 = process.fiber
    chan1 = W_FiberChannel(fiber1)
    fiber2 = process.create_fiber()
    chan2 = W_FiberChannel(fiber2)
    return chan1, chan2


def activate_fiber(process, fiber_wrap, function, args):
    process.activate_fiber(fiber_wrap.fiber, function, args)


def newcoroutine(process, fn):
    chan1, chan2 = open_fiber_channel(process)
    return W_Coroutine(fn, chan1, chan2)
