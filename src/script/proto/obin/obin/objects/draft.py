__author__ = 'gloryofrobots'
class W_Array(W_Cell):
    _type_ = 'Array'
    _immutable_fields_ = ['__length']

    def __init__(self, items=None):
        super(W_Array, self).__init__()

        if not items:
            items = []
        assert isinstance(items, list)
        self._items = items
        self._length = len(self._items)

    def __str__(self):
        return u'W_Array("%s")' % (self._items)

    def _put_(self, k, v):
        from space import state, isint
        if not isint(k):
            raise JsKeyError("Integer key expected", k)
        i = k.value()
        try:
            self._items[i] = v
        except:
            raise JsKeyError("Invalid index ", k)

    def _at_(self, k):
        from space import state, isint
        if isint(k):
            return self._at_index_(k.value())
        else:
            return api.at(state.traits.Array, k)

    def __str__(self):
        return u'W_Array("%s")' % (self._items)

    def _tostring_(self):
        return str(self._items)

    def _iterator_(self):
        return LinearSequenceIterator(self, self._length)

    def _tobool_(self):
        return bool(self._items)

    def _length_(self):
        return self._length

    def at(self, i):
        return self._items[i]

    def _at_index_(self, index):
        from space import newundefined
        try:
            el = self._items[index]
        except KeyError:
            return newundefined()

        return el

class W_Tuple(W_Array):
    _type_ = 'Tuple'
    _immutable_fields_ = ['__length']

    def __init__(self, items):
        super(W_Tuple, self).__init__()
        assert isinstance(items, list)
        self._items = tuple(items)
        self._length = len(self._items)

    def __str__(self):
        return u'W_Tuple("%s")' % str(self._items)

    def _put(self, k, v):
        raise NotImplementedError()

    def _at_(self, k):
        from space import state, isint
        if isint(k):
            return self._at_index_(k.value())
        else:
            return api.at(state.traits.Tuple, k)
