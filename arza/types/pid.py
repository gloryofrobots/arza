from arza.types.root import W_Callable
from arza.runtime import error
from arza.types import api, space


class W_PID(W_Callable):

    def __init__(self, process):
        self.process = process

    def _to_string_(self):
        return "<PID %d>" % self.process.id

    def _to_repr_(self):
        return self._to_string_()

    def _type_(self, process):
        return process.std.types.Function

    def _call_(self, process, args):
        self.process.receive(args)

    def _equal_(self, other):
        from arza.types import space
        if not space.ispid(other):
            return False

        return id(self) == id(other)
        # return api.equal_b(self.process.id, other.process.id)


def newpid(process):
    return W_PID(process)
