from arza.types import string, space, api
from arza.runtime.routine.routine import complete_native_routine
from arza.runtime import error


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_string')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'to_list', to_list, 1)
    api.put_native_function(process, _module, u'reverse', reverse, 1)
    api.put_native_function(process, _module, u'slice', slice, 3)
    api.put_native_function(process, _module, u'take', take, 2)
    api.put_native_function(process, _module, u'drop', drop, 2)
    api.put_native_function(process, _module, u'concat', concat, 2)
    api.put_native_function(process, _module, u'append', append, 2)
    api.put_native_function(process, _module, u'prepend', prepend, 2)
    api.put_native_function(process, _module, u'split', split, 2)
    api.put_native_function(process, _module, u'replace', replace, 3)
    api.put_native_function(process, _module, u'replace_first', replace_first, 3)

    _module.export_all()
    process.modules.add_module(_module_name, _module)


@complete_native_routine
def to_list(process, routine):
    arg0 = routine.get_arg(0)

    return string.to_list(arg0)


@complete_native_routine
def reverse(process, routine):
    arg0 = routine.get_arg(0)

    return string.reverse(arg0)


@complete_native_routine
def slice(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = api.to_i(routine.get_arg(1))

    arg0 = api.to_i(routine.get_arg(0))

    return string.slice(arg2, arg0, arg1)


@complete_native_routine
def take(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = api.to_i(routine.get_arg(0))

    return string.take(arg1, arg0)


@complete_native_routine
def drop(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = api.to_i(routine.get_arg(0))

    return string.drop(arg1, arg0)


@complete_native_routine
def concat(process, routine):
    arg0 = routine.get_arg(0)

    arg1 = routine.get_arg(1)

    return string.concat(arg0, arg1)


@complete_native_routine
def append(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return string.append(arg1, arg0)


@complete_native_routine
def prepend(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return string.prepend(arg1, arg0)


@complete_native_routine
def split(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return string.split(arg1, arg0)


@complete_native_routine
def replace(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return string.replace(arg2, arg0, arg1)


@complete_native_routine
def replace_first(process, routine):
    arg2 = routine.get_arg(2)

    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return string.replace_first(arg2, arg0, arg1)
