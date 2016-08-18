from lalan.types import space, api, datatype
from lalan.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'lalan:lang:_datatype')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'record_keys', record_keys, 1)
    api.put_native_function(process, _module, u'record_values', record_values, 1)
    api.put_native_function(process, _module, u'record_index_of', record_index_of, 2)

    _module.export_all()
    process.modules.add_module(_module_name, _module)


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
