from obin.objects.object_space import hide_on_translate
from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
#from pypy.rlib import jit
from obin.objects import api

def setup_builtins(interpreter, obj):
    pass



@complete_native_routine
def js_load(routine):
    from obin.objects.object_space import object_space
    from obin.runtime.interpreter import load_file
    filename = routine.get_arg(0).value()
    src = load_file(str(filename))
    object_space.interpreter.run_src(src)


@complete_native_routine
@hide_on_translate
def js_trace(routine):
    import pdb
    pdb.set_trace()


@complete_native_routine
def js_debug(routine):
    from obin.objects.object_space import object_space
    config = object_space.interpreter.config
    config.debug = not config.debug
    return config.debug
