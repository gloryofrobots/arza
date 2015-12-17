from obin.objects.space import _w
from obin.runtime.routine import complete_native_routine
from obin.objects.object import W_Boolean
from obin.runtime.exception import ObinTypeError


def setup(trait):
    from obin.builtins import put_property, put_native_function
    from obin.objects.space import state

    # 15.6.2
    from obin.objects.object import W__Object
    w_Boolean = W__Object()
    state.assign_proto(w_Boolean, state.proto_function)
    put_property(trait, u'Boolean', w_Boolean)

    # 15.6.3
    put_property(w_Boolean, u'length', _w(1))

    # 15.6.4
    w_BooleanPrototype = W_Boolean(False)
    state.assign_proto(w_BooleanPrototype, state.proto_object)

    # 15.6.3.1
    state.proto_boolean = w_BooleanPrototype

    # 15.6.3.1
    put_property(w_Boolean, u'prototype', w_BooleanPrototype)

