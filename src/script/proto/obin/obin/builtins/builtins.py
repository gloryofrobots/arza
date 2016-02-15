
def setup(process, module, stdlib):
    import obin.builtins.setup_traits
    obin.builtins.setup_traits.setup(process, module, stdlib)

    import obin.builtins.generics.setup_generics
    obin.builtins.generics.setup_generics.setup(process, module, stdlib)

    import obin.builtins.prelude
    obin.builtins.prelude.setup(process, module, stdlib)

    # MODULES

    import obin.builtins.modules.module_tvar
    obin.builtins.modules.module_tvar.setup(process, module, stdlib)

    import obin.builtins.modules.module_lists
    obin.builtins.modules.module_lists.setup(process, module, stdlib)

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

