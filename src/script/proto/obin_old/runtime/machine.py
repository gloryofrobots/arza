__author__ = 'gloryofrobots'

class FiberEntry(object):
    def __init__(self, fiber):
        self.fiber = fiber
        self.next = None
        self.previous = None

class Machine(object):
    def __init__(self):
        self.head = None
        self.current = None
        self.__enabled = False

    def enable(self):
        if self.__enabled is True:
            return
        self.__enabled = True
        self.run()

    def disable(self):
        self.__enabled = False

    def addFiber(self, fiber):
        if not self.head:
            self.head = FiberEntry(fiber)
            return

        entry = FiberEntry(fiber)
        entry.next =  self.head
        self.head.previous = entry
        self.head = entry

    def run(self):
        while(True):
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
            state = fiber.state
            if state == fiber.State.SUSPENDED:
                current = current.next
                continue
            if state == fiber.State.TERMINATED:
                current = self.kill_fiber(current)
                continue
            if state == fiber.State.IDLE:
                fiber.activate()

            if fiber.is_active():
                try:
                    fiber.execute()
                except:
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

