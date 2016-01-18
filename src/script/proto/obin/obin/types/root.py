# TODO REFACTOR DICT AND ID
def check_implementation_0(operation_name):
    def _check(f):
        def wrapper(self):
            try:
                return f(self)
            except NotImplementedError:
                from obin.runtime import error
                from obin.types import space
                return error.throw_2(error.Errors.NOT_IMPLEMENTED, space.newstring(unicode(operation_name)), self)

        return wrapper

    return _check

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

def not_implemented_error(name, *args):
    from obin.types import space
    from obin.runtime import error
    if len(args) == 1:
        return error.throw_2(error.Errors.NOT_IMPLEMENTED, space.newstring(name), args[0])
    elif len(args) == 2:
        return error.throw_3(error.Errors.NOT_IMPLEMENTED, space.newstring(name), args[0], args[1])
    elif len(args) == 3:
        return error.throw_4(error.Errors.NOT_IMPLEMENTED, space.newstring(name), args[0], args[1], args[2])
    elif len(args) == 4:
        return error.throw_5(error.Errors.NOT_IMPLEMENTED, space.newstring(name), args[0], args[1], args[2], args[3])
    raise RuntimeError("not_implemented_error for arity not defined", len(args))

class W_Any:
    def __str__(self):
        return self._tostring_()

    def __repr__(self):
        return self.__str__()

    # BEHAVIOR
    def _at_(self, key):
        return not_implemented_error(u"_at_", self, key)

    def _at_index_(self, i):
        return not_implemented_error(u"_at_index_", self, i)

    def _get_index_(self, obj):
        return not_implemented_error(u"_get_index_", self, obj)

    def _put_at_index_(self, i, obj):
        return not_implemented_error(u"_put_at_index_", self, i, obj)

    def _length_(self):
        return not_implemented_error(u"_length_", self)

    def _put_(self, k, v):
        return not_implemented_error(u"_put_", self, k, v)

    def _remove_at_(self, key):
        return not_implemented_error(u"_remove_at_", self, key)

    def _tostring_(self):
        return not_implemented_error(u"_tostring_", self)

    def _tobool_(self):
        return not_implemented_error(u"_tobool_", self)

    def _tointeger_(self):
        return not_implemented_error(u"_tointeger_", self)

    def _tofloat_(self):
        return not_implemented_error(u"_tofloat_", self)

    def _equal_(self, other):
        return not_implemented_error(u"_equal_", self, other)

    def _hash_(self):
        return not_implemented_error(u"_hash_", self)

    def _compare_(self, other):
        return not_implemented_error(u"_compare_", self, other)

    def _call_(self, process, args):
        return not_implemented_error(u"_call_", self, args)

    def _slice_(self, start, end):
        return not_implemented_error(u"_call_", self, start, end)

    def _behavior_(self, process):
        return not_implemented_error(u"_behavior_", self)

    def _compute_hash_(self):
        return not_implemented_error(u"_compute_hash_", self)

    def _to_routine_(self, stack, args):
        return not_implemented_error(u"_to_routine_", args)

    def _clone_(self):
        return not_implemented_error(u"_clone_")


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
        return not_implemented_error(u"_compute_hash_", self)

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

