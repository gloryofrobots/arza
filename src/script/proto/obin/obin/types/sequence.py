from obin.types.root import W_Any
from obin.types import api

class W_SequenceIterator(W_Any):
    def __init__(self, source):
        from obin.types.space import isany
        assert isany(source)
        self.index = 0
        self.source = source
        self.source_length = api.length_i(source)

    def _next_(self):
        from obin.types.space import newnil
        if self.index >= self.source_length:
            return newnil()

        el = api.at_index(self.source, self.index)
        self.index += 1
        return el

    def _to_string_(self):
        return "<Iterator %d:%d>" % (self.index, self.source_length)

    def _to_bool_(self):
        if self.index >= self.source_length:
            return False
        return True

