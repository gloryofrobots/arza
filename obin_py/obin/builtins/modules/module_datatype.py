from obin.types import space, api, datatype
from obin.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    name = space.newsymbol(process, u'obin:lang:_datatype')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'union_to_list', union_to_list, 1)
    api.put_native_function(process, _module, u'get_union', get_union, 1)

    _module.export_all()
    process.modules.add_module(name, _module)


@complete_native_routine
def union_to_list(process, routine):
    union = routine.get_arg(0)
    return datatype.union_to_list(union)


@complete_native_routine
def get_union(process, routine):
    union = routine.get_arg(0)
    return datatype.get_union(process, union)
