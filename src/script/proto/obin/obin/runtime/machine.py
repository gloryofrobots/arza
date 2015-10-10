from fiber import Fiber


class FiberEntry(object):
    def __init__(self, fiber):
        self.fiber = fiber
        self.next = None
        self.previous = None

def run_routine_for_result(routine, ctx=None):
    if ctx:
        routine.set_context(ctx)
    m = Machine()
    result = m.run_with(routine)
    return result

class Machine(object):
    def __init__(self):
        self.head = None
        self.current = None
        self.__enabled = False
        self.result = None

    def enabled(self):
        return self.__enabled

    def enable(self):
        if self.__enabled is True:
            return
        self.__enabled = True

    def disable(self):
        self.__enabled = False

    def add_fiber(self, fiber):
        if not self.head:
            self.head = FiberEntry(fiber)
            return

        entry = FiberEntry(fiber)
        entry.next = self.head
        self.head.previous = entry
        self.head = entry

    def run_with(self, routine):
        from fiber import Fiber
        f = Fiber()
        f.call_routine(routine)
        self.add_fiber(f)
        self.run()
        return f.result

    def run(self):
        self.enable()
        while True:
            if not self.__enabled:
                break

            if not self.head:
                break

            self.__run_fibers()

        self.disable()

    def __run_fibers(self):
        current = self.head
        while True:
            if not self.__enabled or not current:
                break
            fiber = current.fiber
            if fiber.is_suspended():
                current = current.next
                continue
            if fiber.is_terminated():
                current = self.kill_fiber(current)
                continue
            if fiber.is_idle():
                fiber.activate()

            if fiber.is_active():
                try:
                    fiber.execute()
                except Exception as e:
                    self.kill_fiber(current)
                    self.disable()
                    raise

            current = current.next

    def kill_fiber(self, entry):
        previous = entry.previous
        next = entry.next
        if previous is not None and next is not None:
            previous.next = next
            next.previous = previous
            return next

        if previous is None and next is not None:
            next.previous = None
            self.head = next
            return next

        if previous is not None and next is None:
            previous.next = None
            return None

        self.head = None
        return None

