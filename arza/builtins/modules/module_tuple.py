__author__ = 'gloryofrobots'
from arza.types import tuples, space, api
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    from arza.builtins import lang_names
    _module_name = lang_names.get_lang_symbol(process, u"_tuple")
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'slice', slice, 3)
    api.put_native_function(process, _module, u'take', take, 2)
    api.put_native_function(process, _module, u'drop', drop, 2)
    api.put_native_function(process, _module, u'index_of', get_index, 2)
    api.put_native_function(process, _module, u'concat', concat, 2)
    api.put_native_function(process, _module, u'prepend', prepend, 2)
    api.put_native_function(process, _module, u'append', append, 2)
    api.put_native_function(process, _module, u'to_list', _to_list, 1)

    _module.export_all()
    process.modules.add_env(_module)


@complete_native_routine
def slice(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = api.to_i(routine.get_arg(1))
    arg2 = api.to_i(routine.get_arg(2))

    return tuples.slice(arg0, arg1, arg2)


@complete_native_routine
def take(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = api.to_i(routine.get_arg(1))

    return tuples.take(arg0, arg1)


@complete_native_routine
def drop(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = api.to_i(routine.get_arg(1))

    return tuples.drop(arg0, arg1)


@complete_native_routine
def get_index(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return api.get_index(arg0, arg1)


@complete_native_routine
def concat(process, routine):
    arg0 = routine.get_arg(0)

    arg1 = routine.get_arg(1)

    return tuples.concat(arg0, arg1)


@complete_native_routine
def prepend(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return tuples.prepend(arg0, arg1)


@complete_native_routine
def append(process, routine):
    arg0 = routine.get_arg(0)
    arg1 = routine.get_arg(1)

    return tuples.append(arg0, arg1)


@complete_native_routine
def _to_list(process, routine):
    arg0 = routine.get_arg(0)

    return tuples.to_list(arg0)
