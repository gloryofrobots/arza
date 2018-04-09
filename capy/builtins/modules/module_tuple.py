__author__ = 'gloryofrobots'
from capy.types import tuples, space, api
from capy.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_tuple')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'slice', slice, 3)
    api.put_native_function(process, _module, u'take', take, 2)
    api.put_native_function(process, _module, u'drop', drop, 2)
    api.put_native_function(process, _module, u'index_of', get_index, 2)
    api.put_native_function(process, _module, u'concat', concat, 2)
    api.put_native_function(process, _module, u'prepend', prepend, 2)
    api.put_native_function(process, _module, u'to_list', _to_list, 1)

    _module.export_all()
    process.classes.add_env(_module)


@complete_native_routine
def slice(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = api.to_i(routine.get_arg(1))

    arg0 = api.to_i(routine.get_arg(0))

    return tuples.slice(arg2, arg0, arg1)


@complete_native_routine
def take(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = api.to_i(routine.get_arg(0))

    return tuples.take(arg1, arg0)


@complete_native_routine
def drop(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = api.to_i(routine.get_arg(0))

    return tuples.drop(arg1, arg0)


@complete_native_routine
def get_index(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return api.get_index(arg1, arg0)


@complete_native_routine
def concat(process, routine):
    arg0 = routine.get_arg(0)

    arg1 = routine.get_arg(1)

    return tuples.concat(arg0, arg1)


@complete_native_routine
def prepend(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return tuples.prepend(arg1, arg0)


@complete_native_routine
def _to_list(process, routine):
    arg0 = routine.get_arg(0)

    return tuples.to_list(arg0)
