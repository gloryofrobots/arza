# TODO REFACTOR DICT AND ID

class W_Root:
    def __str__(self):
        return self._tostring_()

    def __repr__(self):
        return self.__str__()

    # BEHAVIOR
    def _at_(self, b):
        raise NotImplementedError()

    def _at_index_(self, i):
        raise NotImplementedError()

    def _get_index_(self, obj):
        raise NotImplementedError()

    def _put_at_index_(self, i, obj):
        raise NotImplementedError()

    def _length_(self):
        raise NotImplementedError()

    def _put_(self, k, v):
        raise NotImplementedError()

    def _remove_at_(self, key):
        raise NotImplementedError()

    def _tostring_(self):
        raise NotImplementedError()

    def _tobool_(self):
        raise NotImplementedError()

    def _tointeger_(self):
        raise NotImplementedError()

    def _tofloat_(self):
        raise NotImplementedError()

    def _equal_(self, other):
        raise NotImplementedError()

    def _hash_(self):
        raise NotImplementedError()

    def _compare_(self, other):
        raise NotImplementedError()

    def _call_(self, process, args):
        raise NotImplementedError()

    def _kindof_(self, trait):
        raise NotImplementedError()

    def _slice_(self, start, end, step):
        raise NotImplementedError()

    def _traits_(self, process):
        raise NotImplementedError()

    def _totrait_(self, process):
        raise NotImplementedError()

    def _compute_hash_(self):
        raise NotImplementedError()

    def _to_routine_(self, args):
        raise NotImplementedError()

    def _clone_(self):
        raise NotImplementedError()

class W_Cell(W_Root):
    def __init__(self):
        self.__frozen = False

    def freeze(self):
        self.__frozen = True

    def isfrozen(self):
        return self.__frozen


class W_Hashable(W_Root):
    def __init__(self):
        self.__hash = None

    def _compute_hash_(self):
        raise NotImplementedError()

    def _hash_(self):
        if self.__hash is None:
            self.__hash = self._compute_hash_()
        return self.__hash


class W_Callable(W_Root):
    def _to_routine_(self, args):
        raise NotImplementedError()


class W_ValueType(W_Root):
    pass


# TODO RENAME
class W_Constant(W_Root):
    pass
