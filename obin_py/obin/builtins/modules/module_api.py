from obin.types import api, space
from obin.runtime import error
from obin.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'obin:lang:_api')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'length', length, 1)
    api.put_native_function(process, _module, u'is_empty', is_empty, 1)
    api.put_native_function(process, _module, u'put', put, 3)
    api.put_native_function(process, _module, u'at', at, 2)
    api.put_native_function(process, _module, u'elem', elem, 2)
    api.put_native_function(process, _module, u'del', delete, 2)
    api.put_native_function(process, _module, u'equal', equal, 2)
    api.put_native_function(process, _module, u'to_string', to_string, 1)
    api.put_native_function(process, _module, u'to_repr', to_repr, 1)

    _module.export_all()
    process.modules.add_module(_module_name, _module)


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

    return api.put(arg2, arg0, arg1)


@complete_native_routine
def at(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.at(arg1, arg0)


@complete_native_routine
def elem(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.contains(arg1, arg0)


@complete_native_routine
def delete(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.delete(arg1, arg0)


@complete_native_routine
def equal(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.equal(arg1, arg0)


@complete_native_routine
def to_string(process, routine):
    arg0 = routine.get_arg(0)

    return api.to_string(arg0)


@complete_native_routine
def to_repr(process, routine):
    arg0 = routine.get_arg(0)

    return api.to_repr(arg0)
