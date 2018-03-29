from arza.types import api, space
from arza.runtime import error
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_std_behavior')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'len', length, 1)
    api.put_native_function(process, _module, u'is_empty', is_empty, 1)
    api.put_native_function(process, _module, u'put', put, 3)
    api.put_native_function(process, _module, u'at', at, 2)
    api.put_native_function(process, _module, u'has', has, 2)
    api.put_native_function(process, _module, u'del', delete, 2)
    api.put_native_function(process, _module, u'equal', equal, 2)
    api.put_native_function(process, _module, u'not_equal', not_equal, 2)
    api.put_native_function(process, _module, u'str', to_string, 1)
    api.put_native_function(process, _module, u'repr', to_repr, 1)
    api.put_native_function(process, _module, u'cast', cast, 2)

    _module.export_all()
    process.modules.add_env(_module)


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
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)
    arg2 = routine.get_arg(2)

    return api.put(arg0, arg1, arg2)


@complete_native_routine
def at(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.at(arg0, arg1)


@complete_native_routine
def cast(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    if not space.islist(arg1):
        arg1 = space.newlist([arg1])
    return space.newmirror(arg0, arg1)


@complete_native_routine
def has(process, routine):
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
