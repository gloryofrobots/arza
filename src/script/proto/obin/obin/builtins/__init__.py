from obin.objects.object_space import _w
from obin.objects import api
#from pypy.rlib import jit



def setup_builtins(global_object):
    from obin.objects.object_space import object_space
    import obin.builtins.object
    target = object_space.traits.Object
    # 15.2.4.2 Object.prototype.toString()
    api.put_native_function(target, u'toString', obin.builtins.object.to_string)
    api.put_native_function(target, u'toLocaleString', obin.builtins.object.to_string)

    # 15.2.4.3 Object.prototype.valueOf()
    api.put_native_function(target, u'valueOf', obin.builtins.object.value_of)
    api.put_native_function(target, u'clone', obin.builtins.object.clone)
    api.put_native_function(target, u'hasOwnProperty', obin.builtins.object.has_own_property)
    api.put_native_function(target, u'create', obin.builtins.object.create)

    # target = object_space.traits.Function
    # # 15.3.4.2 Function.prototype.toString()
    # api.put_native_function(target, u'toString', obin.builtins.function.to_string)
    #
    # # 15.3.4.3 Function.prototype.apply
    # api.put_native_function(target, u'apply', obin.builtins.function.js_apply)
    #
    # # 15.3.4.4 Function.prototype.call
    # api.put_native_function(target, u'call', obin.builtins.function.js_call)

    import obin.builtins.global_functions
    obin.builtins.global_functions.setup(global_object)
    """
    import obin.builtins.boolean
    obin.builtins.boolean.setup(global_object)

    import obin.builtins.number
    obin.builtins.number.setup(global_object)

    import obin.builtins.string
    obin.builtins.string.setup(global_object)

    import obin.builtins.array
    obin.builtins.array.setup(global_object)

    import obin.builtins.math_functions
    obin.builtins.math_functions.setup(global_object)

    """

from obin.objects.object_space import newundefined


def get_arg(args, index, default=newundefined()):
    if len(args) > index:
        return args[index]
    return default
