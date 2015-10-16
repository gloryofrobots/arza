from obin.objects.object_space import _w

#from pypy.rlib import jit


def new_native_function(function, name=u'', params=[]):
    from obin.runtime.routine import NativeRoutine
    from obin.objects.object_space import object_space

    jsfunc = NativeRoutine(function, name)
    obj = object_space.new_func(jsfunc, formal_parameter_list=params)
    return obj


# 15
def put_native_function(obj, name, func, params=[]):
    jsfunc = new_native_function(func, name, params)
    put_property(obj, name, jsfunc)


# 15
def put_property(obj, name, value):
    from obin.objects.object import put_property as _put_property
    _put_property(obj, name, value)


def setup_builtins(global_object):
    from obin.objects.object_space import object_space

    # 15.2.4 Properties of the Object Prototype Object
    from obin.objects.object import W_BasicObject
    w_ObjectPrototype = W_BasicObject()
    object_space.proto_object = w_ObjectPrototype

    # 15.3.2
    from obin.objects.object import W__Object
    w_Function = W__Object()
    put_property(global_object, u'Function', w_Function)

    # 15.3.4 Properties of the Function Prototype Object
    from obin.runtime.routine import NativeRoutine

    import obin.builtins.function
    empty_func = NativeRoutine(obin.builtins.function.empty, u'Empty')
    w_FunctionPrototype = object_space.new_func(empty_func)
    object_space.assign_proto(w_FunctionPrototype, object_space.proto_object)
    object_space.proto_function = w_FunctionPrototype

    # 15.3.3
    object_space.assign_proto(w_Function, object_space.proto_object)

    # 15.2 Object Objects
    # 15.2.3 Properties of the Object Constructor
    from obin.objects.object import W__Object
    w_Object = W__Object()
    object_space.assign_proto(w_Object, object_space.proto_object)

    put_property(w_Object, u'length', _w(1))

    put_property(global_object, u'Object', w_Object)

    # 15.2.3.1 Object.prototype
    put_property(w_Object, u'prototype', w_ObjectPrototype)

    import obin.builtins.object
    # 15.2.4.2 Object.prototype.toString()
    put_native_function(w_ObjectPrototype, u'toString', obin.builtins.object.to_string)
    put_native_function(w_ObjectPrototype, u'toLocaleString', obin.builtins.object.to_string)

    # 15.2.4.3 Object.prototype.valueOf()
    put_native_function(w_ObjectPrototype, u'valueOf', obin.builtins.object.value_of)
    put_native_function(w_ObjectPrototype, u'clone', obin.builtins.object.clone)
    put_native_function(w_ObjectPrototype, u'hasOwnProperty', obin.builtins.object.has_own_property)
    put_native_function(w_ObjectPrototype, u'create', obin.builtins.object.create)

    # 15.3 Function Objects
    # 15.3.3 Properties of the Function Constructor

    # 15.3.3.1 Function.prototype
    put_property(w_Function, u'prototype', w_FunctionPrototype)

    # 15.3.3.2 Function.length
    put_property(w_Function, u'length', _w(1))

    # 14.3.4.1 Function.prototype.constructor
    put_property(w_FunctionPrototype, u'constructor', w_Function)

    # 15.3.4.2 Function.prototype.toString()
    put_native_function(w_FunctionPrototype, u'toString', obin.builtins.function.to_string)

    # 15.3.4.3 Function.prototype.apply
    put_native_function(w_FunctionPrototype, u'apply', obin.builtins.function.js_apply)

    # 15.3.4.4 Function.prototype.call
    put_native_function(w_FunctionPrototype, u'call', obin.builtins.function.js_call)

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

    import obin.builtins.global_functions
    obin.builtins.global_functions.setup(global_object)


from obin.objects.object_space import newundefined


def get_arg(args, index, default=newundefined()):
    if len(args) > index:
        return args[index]
    return default
