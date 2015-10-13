from obin.builtins import get_arg
from obin.objects.object_space import w_return, _w, isnull_or_undefined, newundefined


def setup(global_object):
    from obin.builtins import put_property, put_native_function
    from obin.objects.object import W__Object, W__Array
    from obin.objects.object_space import object_space

    w_Array = W__Object()
    object_space.assign_proto(w_Array, object_space.proto_function)
    put_property(global_object, u'Array', w_Array)

    # 15.4.4
    w_ArrayPrototype = W__Array()
    object_space.assign_proto(w_ArrayPrototype, object_space.proto_object)
    object_space.proto_array = w_ArrayPrototype

    # 15.4.3.1
    put_property(w_Array, u'prototype', w_ArrayPrototype)

    # 15.4.4.2
    put_native_function(w_ArrayPrototype, u'toString', to_string)

    # 15.4.4.5
    put_native_function(w_ArrayPrototype, u'join', join, params=[u'separator'])

    # 15.4.4.6
    put_native_function(w_ArrayPrototype, u'pop', pop)

    # 15.4.4.7
    put_native_function(w_ArrayPrototype, u'push', push)

    # 15.4.4.8
    put_native_function(w_ArrayPrototype, u'reverse', reverse)

    # 15.4.4.11
    put_native_function(w_ArrayPrototype, u'sort', sort)
    put_native_function(w_ArrayPrototype, u'length', length)

    put_native_function(w_ArrayPrototype, u'forEach', for_each)

    put_native_function(w_ArrayPrototype, u'indexOf', index_of)

    put_native_function(w_ArrayPrototype, u'lastIndexOf', last_index_of)

    put_native_function(w_ArrayPrototype, u'shift', shift)

    put_native_function(w_ArrayPrototype, u'slice', slice)


@w_return
def slice(this, args):
    o = this.ToObject()
    from_index = get_arg(args, 0).ToUInt32()
    to_index = get_arg(args, 1).ToUInt32()
    from obin.objects.object_space import object_space
    n = object_space.new_array(length=_w(to_index-from_index))
    from obin.objects.object import put_property
    index = 0
    for item in xrange(from_index, to_index):
        put_property(n, unicode(str(index)), o.get(unicode(str(item))))
        index += 1
    return n


# 15.4.4.7
@w_return
def push(this, args):
    o = this.ToObject()
    for item in args:
        e = item
        o._items.append(e)

    return o.length()

def length(this, args):
    o = this.ToObject()
    return o.length()

# 15.4.4.2
@w_return
def to_string(this, args):
    from obin.runtime.machine import run_function_for_result
    array = this.ToObject()
    func = array.get(u'join')
    if func.is_callable():
        from obin.objects.object import W_BasicFunction
        assert isinstance(func, W_BasicFunction)
        result = run_function_for_result(func, this=this)
        return result.to_string()
    else:
        return this.to_string()


# 15.4.4.5
@w_return
def join(this, args):
    from obin.objects.object_space import isundefined

    separator = get_arg(args, 0)

    o = this.ToObject()
    length = o.length()

    if isundefined(separator):
        sep = u','
    else:
        sep = separator.to_string()

    if length == 0:
        return u''

    element0 = o.get(_w(0))
    if isnull_or_undefined(element0):
        r = u''
    else:
        r = element0.to_string()

    k = 1

    while(k < length):
        s = r + sep
        element = o.get(unicode(str(k)))
        if isnull_or_undefined(element):
            _next = u''
        else:
            _next = element.to_string()
        r = s + _next
        k += 1

    return r


# 15.4.4.6
@w_return
def pop(this, args):
    o = this.ToObject()
    return o._items.pop()

@w_return
def shift(this, args):
    o = this.ToObject()
    l = o.get(u'length').ToUInt32()

    if l == 0:
        o.put(u'length', _w(0))
        return newundefined()
    else:
        new_length = l - 1
        element = o.get(u"0")
        for i in xrange(0, new_length):
            indx = unicode(str(i))
            next_indx = unicode(str(i + 1))
            o.put(indx, o.get(next_indx))
        o.put(u'length', _w(new_length))
        return element


# 15.4.4.8
@w_return
def reverse(this, args):
    o = this.ToObject()
    length = o.get(u'length').ToUInt32()

    import math
    middle = int(math.floor(length / 2))

    lower = 0
    while lower != middle:
        upper = length - lower - 1
        lower_p = unicode(str(lower))
        upper_p = unicode(str(upper))
        lower_value = o.get(lower_p)
        upper_value = o.get(upper_p)
        lower_exists = o.has_property(lower_p)
        upper_exists = o.has_property(upper_p)

        if lower_exists is True and upper_exists is True:
            o.put(lower_p, upper_value)
            o.put(upper_p, lower_value)
        elif lower_exists is False and upper_exists is True:
            o.put(lower_p, upper_value)
            o.delete(upper_p)
        elif lower_exists is True and upper_exists is False:
            o.delete(lower_p)
            o.put(upper_p, lower_value)

        lower = lower + 1


@w_return
def last_index_of(this, args):
    obj = this
    elem = get_arg(args, 0)
    length = this.get(u'length').ToUInt32()
    from_index = length

    if len(args) > 1:
        findex = get_arg(args, 1).ToInt32()
        if findex < 0:
            from_index = length + findex
        else:
            from_index = findex

    from obin.objects.object import W_IntNumber
    for i in xrange(from_index, -1, -1):
        y = obj.get(unicode(str(i)))
        if elem == y:
            return W_IntNumber(i)
    return W_IntNumber(-1)


@w_return
def index_of(this, args):
    obj = this
    length = this.get(u'length').ToUInt32()
    elem = get_arg(args, 0)
    from_index = get_arg(args, 1).ToUInt32()

    from obin.objects.object import W_IntNumber
    for i in xrange(from_index, length):
        y = obj.get(unicode(str(i)))
        if elem == y:
            return W_IntNumber(i)
    return W_IntNumber(-1)


def for_each(this, args):
    obj = this
    length = this.get(u'length').ToUInt32()

    callback = get_arg(args, 0)
    from obin.objects.object import W_BasicFunction
    assert isinstance(callback, W_BasicFunction)

    for i in xrange(length):
        x = obj.get(unicode(str(i)))
        callback.Call(args=[x], this=newundefined())


# 15.4.4.11
@w_return
def sort(this, args):
    obj = this
    length = this.get(u'length').ToUInt32()

    comparefn = get_arg(args, 0)

    # TODO check if implementation defined

    # sorts need to be in-place, lets do some very non-fancy bubble sort for starters
    while True:
        swapped = False
        for i in xrange(1, length):
            x = unicode(str(i - 1))
            y = unicode(str(i))
            comp = sort_compare(obj, x, y, comparefn)
            if comp == 1:
                tmp_x = obj.get(x)
                tmp_y = obj.get(y)
                obj.put(x, tmp_y)
                obj.put(y, tmp_x)
                swapped = True
        if not swapped:
            break

    return obj


def sort_compare(obj, j, k, comparefn=newundefined()):
    from obin.objects.object_space import isundefined

    j_string = j
    k_string = k
    has_j = obj.has_property(j)
    has_k = obj.has_property(k)

    if has_j is False and has_k is False:
        return 0
    if has_j is False:
        return 1
    if has_k is False:
        return -1

    x = obj.get(j_string)
    y = obj.get(k_string)

    if isundefined(x) and isundefined(y):
        return 0
    if isundefined(x):
        return 1
    if isundefined(y):
        return -1

    if not isundefined(comparefn):
        if not comparefn.is_callable():
            from obin.runtime.exception import JsTypeError
            raise JsTypeError(u'')

        from obin.objects.object import W_BasicFunction
        assert isinstance(comparefn, W_BasicFunction)
        res = comparefn.Call(args=[x, y], this=newundefined())
        return res.ToInteger()

    x_string = x.to_string()
    y_string = y.to_string()
    if x_string < y_string:
        return -1
    if x_string > y_string:
        return 1
    return 0
