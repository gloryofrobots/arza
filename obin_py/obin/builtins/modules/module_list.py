__author__ = 'gloryofrobots'
from obin.types import plist, space, api
from obin.runtime.routine.routine import complete_native_routine




def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'obin:lang:list')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'length', _length, 1)
    api.put_native_function(process, _module, u'put', put, 3)
    api.put_native_function(process, _module, u'at', at, 2)
    api.put_native_function(process, _module, u'elem', elem, 2)
    api.put_native_function(process, _module, u'del', delete, 2)
    api.put_native_function(process, _module, u'tail', _tail, 1)
    api.put_native_function(process, _module, u'empty', _empty, 0)
    api.put_native_function(process, _module, u'is_empty', _is_empty, 1)
    api.put_native_function(process, _module, u'head', _head, 1)
    api.put_native_function(process, _module, u'cons', _cons, 2)
    api.put_native_function(process, _module, u'slice', slice, 3)
    api.put_native_function(process, _module, u'take', take, 2)
    api.put_native_function(process, _module, u'drop', drop, 2)

    _module.export_all()
    process.modules.add_module(_module_name, _module)

@complete_native_routine
def _length(process, routine):
    arg0 =routine.get_arg(0)

    return api.length(arg0)


@complete_native_routine
def put(process, routine):
    arg2 =routine.get_arg(2)
    arg1 =routine.get_arg(1)
    arg0 =routine.get_arg(0)

    return api.put(arg2, arg0, arg1)


@complete_native_routine
def at(process, routine):
    arg1 =routine.get_arg(1)
    arg0 =routine.get_arg(0)

    return api.at(arg1, arg0)


@complete_native_routine
def elem(process, routine):
    arg1 =routine.get_arg(1)
    arg0 =routine.get_arg(0)

    return api.contains(arg1, arg0)


@complete_native_routine
def delete(process, routine):
    arg1 =routine.get_arg(1)
    arg0 =routine.get_arg(0)

    return api.delete(arg1, arg0)


@complete_native_routine
def _tail(process, routine):
    arg0 =routine.get_arg(0)

    return plist.tail(arg0)


@complete_native_routine
def _empty(process, routine):

    return plist.empty()


@complete_native_routine
def _is_empty(process, routine):
    arg0 =routine.get_arg(0)

    return space.newbool(plist.is_empty(arg0))

@complete_native_routine
def _head(process, routine):
    arg0 =routine.get_arg(0)

    return plist.head(arg0)


@complete_native_routine
def _cons(process, routine):
    arg0 =routine.get_arg(0)
    arg1 =routine.get_arg(1)

    return plist.cons(arg0, arg1)


@complete_native_routine
def slice(process, routine):
    arg2 =routine.get_arg(2)
    arg1 = api.to_i(routine.get_arg(1))
    arg0 = api.to_i(routine.get_arg(0))

    return plist.slice(arg2, arg0, arg1)


@complete_native_routine
def take(process, routine):
    arg1 =routine.get_arg(1)
    arg0 = api.to_i(routine.get_arg(0))

    return plist.take(arg1, arg0)


@complete_native_routine
def drop(process, routine):
    arg1 =routine.get_arg(1)
    arg0 = api.to_i(routine.get_arg(0))

    return plist.drop(arg1, arg0)

