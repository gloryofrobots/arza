from lalan.types import space, api, lazyval
from lalan.runtime.routine.routine import complete_native_routine

def setup(process, stdlib):
    _module_name = space.newsymbol(process, u'lalan:lang:_lazy')
    _module = space.newemptyenv(_module_name)
    api.put_native_function(process, _module, u'is_forced', is_forced, 1)

    _module.export_all()
    process.modules.add_module(_module_name, _module)

@complete_native_routine
def is_forced(process, routine):
    arg0 = routine.get_arg(0)

    return lazyval.is_forced(arg0)
