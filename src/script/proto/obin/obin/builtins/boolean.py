from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.objects.object import W_Boolean
from obin.runtime.exception import JsTypeError


def setup(global_object):
    from obin.builtins import put_property, put_native_function
    from obin.objects.object_space import object_space

    # 15.6.2
    from obin.objects.object import W__Object
    w_Boolean = W__Object()
    object_space.assign_proto(w_Boolean, object_space.proto_function)
    put_property(global_object, u'Boolean', w_Boolean)

    # 15.6.3
    put_property(w_Boolean, u'length', _w(1))

    # 15.6.4
    w_BooleanPrototype = W_Boolean(False)
    object_space.assign_proto(w_BooleanPrototype, object_space.proto_object)

    # 15.6.3.1
    object_space.proto_boolean = w_BooleanPrototype

    # 15.6.3.1
    put_property(w_Boolean, u'prototype', w_BooleanPrototype)

    # 15.6.4.2
    put_native_function(w_BooleanPrototype, u'toString', to_string)

    # 15.6.4.3
    put_native_function(w_BooleanPrototype, u'valueOf', value_of)


# 15.6.4.2
@complete_native_routine
def to_string(ctx, routine):
    this, args = routine.args()
    if isinstance(this, W_Boolean):
        b = this
    else:
        raise JsTypeError(u'')

    if b.to_boolean() is True:
        return u'true'
    else:
        return u'false'


# 15.6.4.3
@complete_native_routine
def value_of(ctx, routine):
    this, args = routine.args()
    if isinstance(this, W_Boolean):
        b = this
    else:
        raise JsTypeError(u'')

    return b
