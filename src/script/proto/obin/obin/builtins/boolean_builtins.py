from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.objects.object import W_Boolean
from obin.runtime.exception import ObinTypeError


def setup(trait):
    from obin.builtins import put_property, put_native_function
    from obin.objects.object_space import object_space

    # 15.6.2
    from obin.objects.object import W__Object
    w_Boolean = W__Object()
    object_space.assign_proto(w_Boolean, object_space.proto_function)
    put_property(trait, u'Boolean', w_Boolean)

    # 15.6.3
    put_property(w_Boolean, u'length', _w(1))

    # 15.6.4
    w_BooleanPrototype = W_Boolean(False)
    object_space.assign_proto(w_BooleanPrototype, object_space.proto_object)

    # 15.6.3.1
    object_space.proto_boolean = w_BooleanPrototype

    # 15.6.3.1
    put_property(w_Boolean, u'prototype', w_BooleanPrototype)

