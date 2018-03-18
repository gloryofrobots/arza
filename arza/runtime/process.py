from arza.types import api, space, string, root
from arza.runtime.stack import Stack
from arza.types import plist
from arza.runtime import error
from arza.misc.timer import Timer

DEFAULT_STACK_SIZE = 32
INFINITE_LOOP = -42


def _print_trace(device, signal, trace):
    if api.is_empty_b(trace):
        return

    builder = string.Builder().add_u(u"Traceback:").nl()
    for record in trace:
        builder.space(4).add(record).nl()

    builder.add_u(u"Signal:").space().add(signal).nl()
    device.write(builder.value())


class Fiber:
    def __init__(self, process, parent):
        self.call_stack = []
        self.routine = None
        self.parent = parent
        self.continuation_fiber = parent
        self.process = process
        self.stack = Stack(DEFAULT_STACK_SIZE)

    def start_work(self, func, args):
        routine = api.to_routine(func, self.stack, args)
        self.routine = routine
        self.routine.activate()

    def is_complete(self):
        if not self.routine:
            return False
        return self.routine.is_complete()

    def is_finished(self):
        if not self.routine:
            return False
        return self.routine.is_closed()

    def is_passive(self):
        if not self.routine:
            return True
        return self.routine.is_suspended()

    def is_active(self):
        if not self.routine:
            return False
        return self.routine.is_inprocess()

    def is_terminated(self):
        if not self.routine:
            return False
        return self.routine.is_terminated()

    def push_into_stack(self, val):
        self.routine.stack.push(val)

    def stop_routine(self):
        self.routine.suspend()

    def resume_routine(self, result):
        self.routine.resume(self.process, result)

    def finalise(self):
        continuation = self.continuation_fiber
        if continuation is None:
            return None

        assert continuation.routine.is_suspended()
        # print "FINALISE",  self.routine, self.routine.result
        continuation.routine.resume(self.process, self.routine.result)
        return continuation

    def call_object(self, obj, args):
        routine = api.to_routine(obj, self.stack, args)
        self.routine.suspend()
        self.call_stack.append(self.routine)
        self.routine = routine
        routine.activate()

    def previous_routine(self):
        if len(self.call_stack) == 0:
            return None
        return self.call_stack[len(self.call_stack) - 1]

    def __pop(self):
        if len(self.call_stack) == 0:
            return None
        self.routine = self.call_stack.pop()
        return self.routine

    def next_routine(self):
        if len(self.call_stack) == 0:
            return None

        result = self.routine.result
        self.routine = self.call_stack.pop()
        self.routine.resume(self.process, result)
        return self.routine

    def catch(self, signal, trace):
        routine = self.routine
        assert routine.is_terminated()
        while not routine.catch(signal):
            info = routine.info()
            trace = plist.cons(info, trace)
            routine = self.__pop()
            if routine is None:
                return False, trace

        return True, trace


class Mailbox:
    def __init__(self):
        self.messages = plist.empty()

    def __str__(self):
        return str(self.messages)

    def push(self, msg):
        self.messages = plist.append(self.messages, msg)

    def pop(self):
        msg, self.messages = plist.split(self.messages)
        return msg

    def empty(self):
        return plist.is_empty(self.messages)


class Process(root.W_Root):
    class State:
        IDLE = 1
        ACTIVE = 2
        WAITING = 3
        COMPLETE = 4
        TERMINATED = 5

    def __init__(self, data):
        from arza.runtime.process_data import ProcessData
        assert isinstance(data, ProcessData)
        self.id = -1
        self.__data = data
        self.__state = None
        self.fibers = []
        self.__fiber = None
        self.result = None
        self.mailbox = Mailbox()
        self.error_print_enabled = True

        self.__idle()

    """
    PUBLIC API
    """

    def pause(self):
        assert self.is_active(), self.__state
        if not self.mailbox.empty():
            return
        # print "PAUSED", self, self.mailbox
        self.__await()
        self.scheduler.unactivate(self)

    def resume(self):
        assert self.is_waiting(), self.__state
        # print "RESUMED", self, self.mailbox
        self.scheduler.wakeup(self)
        self.__active()

    def receive(self, message):
        self.mailbox.push(message)
        if not self.is_waiting():
            return

        self.resume()

    def result_safe(self):
        if self.result is None:
            return space.newunit()

        return self.result

    def set_id(self, id):
        self.id = id

    @property
    def scheduler(self):
        return self.__data.scheduler

    @property
    def modules(self):
        return self.__data.modules

    @property
    def std(self):
        return self.__data.std

    @property
    def symbols(self):
        return self.__data.symbols

    @property
    def io(self):
        return self.__data.io

    @property
    def parser(self):
        return self.__data.parser

    @property
    def fiber(self):
        return self.__fiber

    @fiber.setter
    def fiber(self, f):
        self.__fiber = f

    @property
    def state(self):
        return self.__state

    def set_error_print_enabled(self, val):
        self.error_print_enabled = val

    def is_finished(self):
        return self.is_complete() or self.is_terminated()

    def is_complete(self):
        return self.state == Process.State.COMPLETE

    def is_terminated(self):
        return self.state == Process.State.TERMINATED

    def is_active(self):
        return self.state == Process.State.ACTIVE

    def is_idle(self):
        return self.state == Process.State.IDLE

    def is_waiting(self):
        return self.state == Process.State.WAITING

    def call_object(self, obj, args):
        self.fiber.call_object(obj, args)

    def run_cycles(self, func, args, cycles):
        self.activate(func, args)
        self.scheduler.activate(self)
        self.iterate(cycles)
        return self.result

    def activate(self, func, args):
        assert self.is_idle() or self.is_waiting()
        assert not self.fiber
        self.fiber = self.create_fiber()
        self.fiber.start_work(func, args)
        # with Timer("Process run"):
        self.__active()

    def run(self, func, args):
        return self.run_cycles(func, args, INFINITE_LOOP)

    def spawn(self):
        child = Process(self.__data)
        return child

    def subprocess(self, func, args):
        child = self.spawn()
        child.run(func, args)
        if child.is_terminated():
            return self._catch_or_terminate(child.result)
        return child.result

    def create_fiber(self):
        # fiber = Fiber(self, self.__fiber)
        fiber = Fiber(self, None)
        # DEBUG ONLY
        self.fibers.append(fiber)
        return fiber

    def activate_fiber(self, fiber, func, args):
        assert self.fiber is not fiber
        assert fiber.routine is None
        self.fiber.stop_routine()
        fiber.start_work(func, args)
        self.fiber = fiber

    def set_fiber_continuation(self, fiber):
        assert fiber is not self.fiber
        self.fiber.continuation_fiber = fiber

    def switch_to_fiber(self, fiber, result):
        assert fiber is not self.fiber
        assert not self.fiber.is_finished()

        assert fiber.routine.is_suspended()

        self.fiber.stop_routine()
        fiber.resume_routine(result)
        self.fiber = fiber

    """
    PRIVATE API
    """

    def iterate(self, cycles):
        # if self.id == 42:
        #     print "42", self.__state
        # print "RUN"
        result = None
        while cycles == INFINITE_LOOP or cycles > 0:
            if not self.is_active():
                break
            try:
                result = self.__execute()
            # except Exception as e:
            #     # print "catching some", e
            #     raise
            except error.ArzaError as e:
                # print "catching error", e
                signal = error.convert_to_script_error(self, e)
                result = self._catch_or_terminate(signal)
            except error.ArzaSignal as e:
                # print "catching signal", e
                result = self._catch_or_terminate(e.signal)
            except Exception as e:
                # TODO IF WE ARE TRANSLATED
                # print e
                # self.__terminate()
                # return e
                ae = error.build(error.Errors.RUNTIME_ERROR, [space.newstring(unicode(e))])
                signal = error.convert_to_script_error(self, ae)
                result = self._catch_or_terminate(signal)
                # raise

            if cycles != INFINITE_LOOP:
                cycles -= 1

        if self.is_complete() or self.is_terminated():
            # print "COMPLETE", result
            assert len(self.fibers) == 0
            assert self.fiber is None
            self.result = result

    def __purge_fiber(self, fiber):
        assert fiber.is_finished()
        self.fibers.remove(fiber)

    def __execute(self):
        # print "execute"
        fiber = self.fiber
        routine = fiber.routine
        assert routine
        assert routine.is_inprocess()
        routine.execute(self)
        if self.is_terminated():
            return routine.result

        if routine.is_suspended():
            return None

        if routine.is_complete():
            continuation = fiber.next_routine()
            if continuation is not None:
                return None

            next_fiber = fiber.finalise()
            self.__purge_fiber(fiber)
            if not next_fiber:
                self.__complete()
                return routine.result
            else:
                self.fiber = next_fiber
                return None

        elif routine.is_terminated():
            signal = routine.result
            return self._catch_or_terminate(signal)

        assert False, "NOT REACHABLE"
        # if suspended reach here
        # return None

    def _catch_or_terminate(self, signal):
        catched, trace = self.__catch_signal(signal)
        if not catched:
            self.__terminate_with_signal(signal, trace)
        return signal

    def __catch_signal(self, signal):
        trace = plist.empty()
        if self.fiber is None:
            return False, trace

        while True:
            if not self.fiber.routine.is_terminated():
                self.fiber.routine.terminate(signal)

            result, trace = self.fiber.catch(signal, trace)
            if result is True:
                return True, trace
            next_fiber = self.fiber.finalise()
            self.__purge_fiber(self.fiber)
            if not next_fiber:
                return False, trace
            self.fiber = next_fiber

    def __set_state(self, s):
        self.__state = s

    def __close(self):
        self.fiber = None
        self.fibers = []
        self.scheduler.close(self)

    def __terminate_with_signal(self, signal, trace):
        if self.error_print_enabled:
            _print_trace(self.io.stderr, signal, trace)
        self.__terminate()

    def exit(self, reason):
        self.__terminate()
        self.result = reason

    def __terminate(self):
        self.__close()
        self.__set_state(Process.State.TERMINATED)

    def __complete(self):
        self.__close()
        self.__set_state(Process.State.COMPLETE)

    def __active(self):
        self.__set_state(Process.State.ACTIVE)

    def __await(self):
        self.__set_state(Process.State.WAITING)

    def __idle(self):
        self.__set_state(Process.State.IDLE)

    def _to_string_(self):
        return "<Process %d %s>" % (self.id, str(self.mailbox))

    def _equal_(self, other):
        return self is other
