from rpython.rlib.rfloat import NAN, INFINITY
from obin.runtime.exception import JsRangeError, JsTypeError
from obin.objects.object import W_Number
from obin.objects.object_space import w_return, _w


def setup(global_object):
    from obin.builtins import put_property, put_native_function
    from obin.objects.object_space import object_space

    # 15.7.2
    from obin.objects.object import W__Object
    w_Number = W__Object()
    # object_space.assign_proto(w_Number, object_space.proto_function)
    put_property(global_object, u'Number', w_Number)

    # 15.7.3
    put_property(w_Number, u'length', _w(1))

    # 15.7.4
    w_NumberPrototype = W__Object()
    object_space.assign_proto(w_NumberPrototype, object_space.proto_object)
    object_space.proto_number = w_NumberPrototype

    # 15.7.4.2
    put_native_function(w_NumberPrototype, u'toString', to_string)

    # 15.7.4.4
    put_native_function(w_NumberPrototype, u'valueOf', value_of)

    # 15.7.3.1
    put_property(w_Number, u'prototype', w_NumberPrototype)

    # 15.7.3.2
    put_property(w_Number, u'MAX_VALUE', w_MAX_VALUE)

    # 15.7.3.3
    put_property(w_Number, u'MIN_VALUE', w_MIN_VALUE)

    # 15.7.3.4
    put_property(w_Number, u'NaN', w_NAN)

    # 15.7.3.5
    put_property(w_Number, u'POSITIVE_INFINITY', w_POSITIVE_INFINITY)

    # 15.7.3.6
    put_property(w_Number, u'NEGATIVE_INFINITY', w_NEGATIVE_INFINITY)

# 15.7.3.2
w_MAX_VALUE = _w(1.7976931348623157e308)

# 15.7.3.3
w_MIN_VALUE = _w(5e-320)

# 15.7.3.4
w_NAN = _w(NAN)

# 15.7.3.5
w_POSITIVE_INFINITY = _w(INFINITY)

# 15.7.3.6
w_NEGATIVE_INFINITY = _w(-INFINITY)


# 15.7.4.2
@w_return
def to_string(this, args):
    if len(args) > 0:
        radix = args[0].ToInteger()
        if radix < 2 or radix > 36:
            raise JsRangeError

    if isinstance(this, W_Number):
        num = this
    else:
        raise JsTypeError(u'')

    # TODO radix, see 15.7.4.2
    return num.to_string()


# 15.7.4.4
@w_return
def value_of(this, args):
    if isinstance(this, W_Number):
        num = this
    else:
        raise JsTypeError(u'')

    return num.ToNumber()
