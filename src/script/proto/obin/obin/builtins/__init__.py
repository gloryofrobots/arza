from obin.objects.object_space import _w
from obin.objects import api
#from pypy.rlib import jit



def setup_builtins(global_object):
    from obin.objects.object_space import object_space
    import obin.builtins.object

    # target = object_space.traits.Function
    # # 15.3.4.2 Function.prototype.toString()
    # api.put_native_function(target, u'toString', obin.builtins.function.to_string)
    #
    # # 15.3.4.3 Function.prototype.apply
    # api.put_native_function(target, u'apply', obin.builtins.function.js_apply)
    #
    # # 15.3.4.4 Function.prototype.call
    # api.put_native_function(target, u'call', obin.builtins.function.js_call)

    import obin.builtins.object
    obin.builtins.object.setup(object_space.traits.Object)

    import obin.builtins.global_functions
    obin.builtins.global_functions.setup(global_object)

    import obin.builtins.vector
    obin.builtins.vector.setup(object_space.traits.Vector)

    import obin.builtins.function
    obin.builtins.function.setup(object_space.traits.Function)

    """
    import obin.builtins.boolean
    obin.builtins.boolean.setup(global_object)

    import obin.builtins.number
    obin.builtins.number.setup(global_object)

    import obin.builtins.string
    obin.builtins.string.setup(global_object)


    import obin.builtins.math_functions
    obin.builtins.math_functions.setup(global_object)

    """

def get_arg(args, index):
    from obin.runtime.exception import ObinInvokeError
    if len(args) > index:
        return args[index]
    raise ObinInvokeError(index)