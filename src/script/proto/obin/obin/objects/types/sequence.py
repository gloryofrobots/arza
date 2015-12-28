from obin.objects.types.root import W_Root
from obin.objects import api

class W_SequenceIterator(W_Root):
    def __init__(self, source):
        from obin.objects.space import isany
        assert isany(source)
        self.index = 0
        self.source = source
        self.source_length = api.n_length(source)

    def _next_(self):
        from obin.objects.space import newundefined
        if self.index >= self.source_length:
            return newundefined()

        el = api.at_index(self.source, self.index)
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.source_length)

    def _tobool_(self):
        if self.index >= self.source_length:
            return False
        return True

