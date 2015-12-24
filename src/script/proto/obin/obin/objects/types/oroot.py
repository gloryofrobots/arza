# TODO REFACTOR DICT AND ID

class W_Root:
    def __str__(self):
        return self._tostring_()

    def __repr__(self):
        return self.__str__()

    def id(self):
        return str(hex(id(self)))

    # BEHAVIOR
    def _at_(self, b):
        raise NotImplementedError()

    def _lookup_(self, b):
        raise NotImplementedError()

    def _length_(self):
        raise NotImplementedError()

    def _put_(self, k, v):
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

    def _call_(self, routine, args):
        raise NotImplementedError()

    def _compare_(self, other):
        raise NotImplementedError()

    def _find_method_for_self_(self, other):
        raise NotImplementedError()

class W_Cell(W_Root):
    def __init__(self):
        self.__frozen = False

    def freeze(self):
        self.__frozen = True

    def unfreeze(self):
        self.__frozen = False

    def isfrozen(self):
        return self.__frozen

