from arza.types import space, api, datatype
from arza.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_datatype')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'record_keys', record_keys, 1)
    api.put_native_function(process, _module, u'record_values', record_values, 1)
    api.put_native_function(process, _module, u'record_index_of', record_index_of, 2)
    api.put_native_function(process, _module, u'has_consructor', has_constructor, 1)
    api.put_native_function(process, _module, u'get_consructor', get_constructor, 1)

    _module.export_all()
    process.modules.add_env(_module)


@complete_native_routine
def has_constructor(process, routine):
    _type = routine.get_arg(0)
    return datatype.has_constructor(_type)


@complete_native_routine
def get_constructor(process, routine):
    _type = routine.get_arg(0)

    return datatype.get_constructor(_type)


@complete_native_routine
def record_keys(process, routine):
    arg0 = routine.get_arg(0)

    return datatype.record_keys(arg0)


@complete_native_routine
def record_values(process, routine):
    arg0 = routine.get_arg(0)

    return datatype.record_values(arg0)


@complete_native_routine
def record_index_of(process, routine):
    arg1 = routine.get_arg(1)

    arg0 = routine.get_arg(0)

    return datatype.record_index_of(arg1, arg0)
