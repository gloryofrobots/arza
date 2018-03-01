from arza.types.root import W_Callable
from arza.runtime import error
from arza.types import api, space


class W_PID(W_Callable):
    def __init__(self, process):
        self.process = process

    def _to_string_(self):
        return "<PID %d:%d>" % (self.process.id, self.process.state)

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.PID

    def _hash_(self):
        return id(self)

    def receive(self, sender_process, message):
        # print "PID CALL", self.process, args
        # process.fiber.push_into_stack(space.newunit())
        self.process.receive(message)

    def _equal_(self, other):
        from arza.types import space
        if not space.ispid(other):
            return False

        return id(self) == id(other)
        # return api.equal_b(self.process.id, other.process.id)


def newpid(process):
    return W_PID(process)
