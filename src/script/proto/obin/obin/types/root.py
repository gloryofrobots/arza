# TODO REFACTOR DICT AND ID
def check_implementation_1(operation_name):
    def _check(f):
        def wrapper(self, arg1):
            try:
                return f(self, arg1)
            except NotImplementedError:
                from obin.runtime import error
                from obin.types import space
                return error.throw_3(error.Errors.NOT_IMPLEMENTED, space.newstring(unicode(operation_name)), self, arg1)

        return wrapper

    return _check


def check_implementation_2(operation_name):
    def _check(f):
        def wrapper(self, arg1, arg2):
            try:
                return f(self, arg1, arg2)
            except NotImplementedError:
                from obin.runtime import error
                from obin.types import space
                return error.throw_4(error.Errors.NOT_IMPLEMENTED,
                                     space.newstring(unicode(operation_name)), self, arg1, arg2)

        return wrapper

    return _check


def check_implementation_3(operation_name):
    def _check(f):
        def wrapper(self, arg1, arg2, arg3):
            try:
                return f(self, arg1, arg2, arg3)
            except NotImplementedError:
                from obin.runtime import error
                from obin.types import space
                return error.throw_5(error.Errors.NOT_IMPLEMENTED,
                                     space.newstring(unicode(operation_name)),
                                     self, arg1, arg2, arg3)

        return wrapper

    return _check


class W_Any:
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

    def _slice_(self, start, end):
        raise NotImplementedError()

    def _behavior_(self, process):
        raise NotImplementedError()

    def _compute_hash_(self):
        raise NotImplementedError()

    def _to_routine_(self, stack, args):
        raise NotImplementedError()

    def _clone_(self):
        raise NotImplementedError()


class W_Cell(W_Any):
    def __init__(self):
        self.__frozen = False

    def freeze(self):
        self.__frozen = True

    def isfrozen(self):
        return self.__frozen


class W_Hashable(W_Any):
    def __init__(self):
        self.__hash = None

    def _compute_hash_(self):
        raise NotImplementedError()

    def _hash_(self):
        if self.__hash is None:
            self.__hash = self._compute_hash_()
        return self.__hash


class W_Callable(W_Any):
    pass


class W_ValueType(W_Any):
    pass


class W_Number(W_ValueType):
    pass


class W_UniqueType(W_Any):
    def _equal_(self, other):
        return self is other

    pass
