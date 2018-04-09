from capy.types import api, space
from capy.runtime import error
from capy.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _class = stdlib.classes.Object
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_method(process, _class, u'type', _type, 1)
    api.put_native_method(process, _class, u'parent', _parent, 1)
    api.put_native_method(process, _class, u'__not__', _not, 1)
    api.put_native_method(process, _class, u'__is__', _is, 2)
    api.put_native_method(process, _class, u'__len__', length, 1)
    api.put_native_method(process, _class, u'__is_empty__', is_empty, 1)
    api.put_native_method(process, _class, u'__put__', put, 3)
    api.put_native_method(process, _class, u'__put_default__', put_default, 3)
    api.put_native_method(process, _class, u'__at__', at, 2)
    api.put_native_method(process, _class, u'__elem__', elem, 2)
    api.put_native_method(process, _class, u'__del__', delete, 2)
    api.put_native_method(process, _class, u'__eq__', equal, 2)
    api.put_native_method(process, _class, u'__ne__', not_equal, 2)
    api.put_native_method(process, _class, u'__str__', to_string, 1)
    api.put_native_method(process, _class, u'__repr__', to_repr, 1)
    api.put_native_method(process, _class, u'__seq__', _seq, 1)
    api.put_native_method(process, _class, u'__head__', _head, 1)
    api.put_native_method(process, _class, u'__tail__', _tail, 1)


@complete_native_routine
def _is(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)
    return space.newbool(arg0 is arg1)


@complete_native_routine
def _type(process, routine):
    arg0 = routine.get_arg(0)
    return api.get_type(process, arg0)


@complete_native_routine
def _parent(process, routine):
    arg0 = routine.get_arg(0)
    t = api.get_type(process, arg0)
    if not space.isclass(t):
        return space.newnil()
    else:
        return t.super


@complete_native_routine
def _not(process, routine):
    arg0 = routine.get_arg(0)
    return api.not_(arg0)


@complete_native_routine
def length(process, routine):
    arg0 = routine.get_arg(0)

    return api.length(arg0)


@complete_native_routine
def is_empty(process, routine):
    arg0 = routine.get_arg(0)

    return api.is_empty(arg0)


@complete_native_routine
def put(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.put(arg0, arg1, arg2)


@complete_native_routine
def put_default(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    existed = api.lookup(arg0, arg1, space.newvoid())
    if space.isvoid(existed):
        return api.put(arg0, arg1, arg2)
    else:
        return arg0


@complete_native_routine
def at(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.at(arg0, arg1)


@complete_native_routine
def elem(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.contains(arg0, arg1)


@complete_native_routine
def delete(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.delete(arg0, arg1)


@complete_native_routine
def equal(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.equal(arg0, arg1)


@complete_native_routine
def not_equal(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.not_equal(arg0, arg1)


@complete_native_routine
def to_string(process, routine):
    arg0 = routine.get_arg(0)

    return api.to_string(arg0)


@complete_native_routine
def to_repr(process, routine):
    arg0 = routine.get_arg(0)

    return api.to_repr(arg0)


@complete_native_routine
def _seq(process, routine):
    arg0 = routine.get_arg(0)

    return api.seq(arg0)


@complete_native_routine
def _head(process, routine):
    arg0 = routine.get_arg(0)

    return api.head(arg0)


@complete_native_routine
def _tail(process, routine):
    arg0 = routine.get_arg(0)

    return api.tail(arg0)
