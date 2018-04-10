from capy.types import api, space, array
from capy.runtime import error
from capy.runtime.routine.routine import complete_native_routine
from capy.builtins.classes.setup_object import _true


def setup(process, stdlib):
    _class = stdlib.classes.Array
    setup_class(process, _class)


def setup_class(process, _class):
    api.put_native_method(process, _class, u'empty', _empty, 0)
    api.put_native_method(process, _class, u'slice', slice, 3)
    api.put_native_method(process, _class, u'take', take, 2)
    api.put_native_method(process, _class, u'drop', drop, 2)
    api.put_native_method(process, _class, u'index_of', get_index, 2)
    api.put_native_method(process, _class, u'concat', concat, 2)
    api.put_native_method(process, _class, u'append', append, 2)
    api.put_native_method(process, _class, u'prepend', prepend, 2)
    api.put_native_method(process, _class, u'is_array', _true, 1)


@complete_native_routine
def _empty(process, routine):
    return array.empty()


@complete_native_routine
def slice(process, routine):
    arg0 = api.to_i(routine.get_arg(0))
    arg1 = api.to_i(routine.get_arg(1))
    arg2 = routine.get_arg(2)

    return array.slice(arg0, arg1, arg2)


@complete_native_routine
def take(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = api.to_i(routine.get_arg(1))

    return array.take(arg0, arg1)


@complete_native_routine
def drop(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = api.to_i(routine.get_arg(1))

    return array.drop(arg0, arg1)


@complete_native_routine
def get_index(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.get_index(arg0, arg1)


@complete_native_routine
def concat(process, routine):
    arg0 = routine.get_arg(0)

    arg1 = routine.get_arg(1)

    return array.concat(arg0, arg1)


@complete_native_routine
def append(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return array.append(arg0, arg1)


@complete_native_routine
def prepend(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return array.prepend(arg0, arg1)
