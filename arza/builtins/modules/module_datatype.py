from arza.types import space, api, datatype
from arza.runtime.routine.routine import complete_native_routine
from arza.runtime import error


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'arza:lang:_datatype')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'record_keys', record_keys, 1)
    api.put_native_function(process, _module, u'record_values', record_values, 1)
    api.put_native_function(process, _module, u'record_index_of', record_index_of, 2)
    api.put_native_function(process, _module, u'has_init', has_init, 1)
    api.put_native_function(process, _module, u'get_init', get_init, 1)
    api.put_native_function(process, _module, u'set_init', set_init, 2)
    api.put_native_function(process, _module, u'finalize_type', finalize_type, 1)

    _module.export_all()
    process.modules.add_env(_module)


@complete_native_routine
def has_init(process, routine):
    _type = routine.get_arg(0)
    return space.newbool(datatype.has_init(_type))


@complete_native_routine
def get_init(process, routine):
    _type = routine.get_arg(0)

    return datatype.get_init(_type)


@complete_native_routine
def set_init(process, routine):
    _type = routine.get_arg(0)
    construct = routine.get_arg(1)
    error.affirm_type(_type, space.isdatatype)
    error.affirm_type(construct, space.isfunction)
    datatype.set_init(_type, construct)
    return _type



@complete_native_routine
def finalize_type(process, routine):
    _type = routine.get_arg(0)
    error.affirm_type(_type, space.isdatatype)
    datatype.finalize_type(_type)
    return _type

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
