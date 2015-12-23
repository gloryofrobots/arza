from obin.runtime.exception import ObinReferenceError


class References(object):
    _virtualizable2_ = ['_refs_[*]']
    _settled_ = True

    def __init__(self, env, size):
        self._refs_ = [None] * size
        self._resizable_ = not bool(size)
        self.env = env

    def _resize_refs(self, index):
        if index >= len(self._refs_):
            self._refs_ += ([None] * (1 + index - len(self._refs_)))

    def _get_refs(self, index):
        assert index < len(self._refs_)
        assert index >= 0

        if self._resizable_:
            self._resize_refs(index)

        return self._refs_[index]

    def _set_refs(self, index, value):
        if self._resizable_:
            self._resize_refs(index)
        assert index < len(self._refs_)
        assert index >= 0
        self._refs_[index] = value

    def store_ref(self, symbol, index, value):
        ref = self._get_refs(index)

        if ref is not None:
            ref.put_value(value)
            return

        ref = self.env.get_reference(symbol)
        if not ref:
            raise ObinReferenceError(symbol)

        ref.put_value(value)
        self._set_refs(index, ref)

    def get_ref(self, symbol, index):
        print "get_ref", symbol, index, self._refs_
        ref = self._get_refs(index)
        print "ref", ref, ref is None
        if ref is None:
            print "is None"
            ref = self.env.get_reference(symbol)
            print " new ref", ref
            # assert ref is not None
            if not ref:
                raise RuntimeError("Unknown reference", (symbol,))
            self._set_refs(index, ref)

        print "ref_get_value"
        return ref.get_value()


class Reference:
    _immutable_fields_ = ['env', 'name', 'index']
    _settled_ = True

    def __init__(self, env, referenced, index):
        assert env is not None
        self.env = env
        self.name = referenced
        self.index = index

    def get_value(self):
        print "Reference.ref_get_value", self.env, self.index
        return self.env.get_local(self.index)

    def put_value(self, value):
        self.env.set_local(self.index, value)
