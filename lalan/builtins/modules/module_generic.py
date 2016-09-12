from lalan.types import api, space
from lalan.types.dispatch import generic
from lalan.runtime import error
from lalan.runtime.routine.routine import complete_native_routine


def setup(process, stdlib):
    name = space.newsymbol(process, u'lalan:lang:_generic')
    _module = space.newemptyenv(name)
    api.put_native_function(process, _module, u'get_method', _method, 2)
    api.put_native_function(process, _module, u'get_types', _types, 1)
    _module.export_all()
    process.modules.add_module(name, _module)


@complete_native_routine
def _method(process, routine):
    types = routine.get_arg(0)
    gf = routine.get_arg(1)
    return generic.get_method(process, gf, types)

@complete_native_routine
def _types(process, routine):
    gf = routine.get_arg(0)
    return gf.get_types()
