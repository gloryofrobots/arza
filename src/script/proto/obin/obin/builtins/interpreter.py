from obin.objects.object_space import hide_on_translate
from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
#from pypy.rlib import jit


def setup_builtins(global_object):
    from obin.builtins import put_native_function

    put_native_function(global_object, u'load', js_load)
    put_native_function(global_object, u'debug', js_debug)
    put_native_function(global_object, u'trace', js_trace)


@complete_native_routine
def js_load(ctx, routine):
    this, args = routine.args()
    from obin.objects.object_space import object_space
    from obin.runtime.interpreter import load_file
    filename = args[0].to_string()
    src = load_file(str(filename))
    object_space.interpreter.run_src(src)


@complete_native_routine
@hide_on_translate
def js_trace(ctx, routine):
    import pdb
    pdb.set_trace()


@complete_native_routine
def js_debug(ctx, routine):
    from obin.objects.object_space import object_space
    config = object_space.interpreter.config
    config.debug = not config.debug
    return config.debug
