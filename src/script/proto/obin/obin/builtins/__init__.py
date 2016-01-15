#from pypy.rlib import jit



def setup_builtins(process):
    # import obin.builtins.object_builitns

    # target = object_space.traits.Function
    # # 15.3.4.2 Function.prototype.toString()
    # api.put_native_function(target, u'toString', obin.builtins.function.to_string)
    #
    # # 15.3.4.3 Function.prototype.apply
    # api.put_native_function(target, u'apply', obin.builtins.function.js_apply)
    #
    # # 15.3.4.4 Function.prototype.call
    # api.put_native_function(target, u'call', obin.builtins.function.js_call)
    module = process.builtins
    stdlib = process.std

    import obin.builtins.setup_traits
    obin.builtins.setup_traits.setup(process, module, stdlib)

    import obin.builtins.setup_generics
    obin.builtins.setup_generics.setup(process, module, stdlib)

    import obin.builtins.setup_globals
    obin.builtins.setup_globals.setup(process, module, stdlib)

    # import obin.builtins.object_builitns
    # obin.builtins.object_builitns.setup(object_space.traits.Object)

    # import obin.builtins.vector_builtins
    # obin.builtins.vector_builtins.setup(object_space.traits.Vector)
    #
    # import obin.builtins.function_builtins
    # obin.builtins.function_builtins.setup(object_space.traits.Function)

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

