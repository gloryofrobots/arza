from obin.objects.object_space import _w
from obin.runtime.routine import complete_native_routine
from obin.builtins import get_arg
from obin.objects.object_space import isnull_or_undefined, newundefined
from obin.objects import api


def setup(obj):
    # 15.4.4.5
    api.put_native_function(obj, u'join', join, 2)

    # 15.4.4.6
    api.put_native_function(obj, u'pop', pop, 1)

    # 15.4.4.7
    api.put_native_function(obj, u'push', push, 2)

    # 15.4.4.8
    api.put_native_function(obj, u'reverse', reverse, 1)

    # 15.4.4.11
    api.put_native_function(obj, u'sort', sort, 1)
    api.put_native_function(obj, u'length', length, 1)

    api.put_native_function(obj, u'forEach', for_each, 2)

    api.put_native_function(obj, u'indexOf', index_of, 2)

    api.put_native_function(obj, u'lastIndexOf', last_index_of, 2)

    api.put_native_function(obj, u'shift', shift, 2)

    api.put_native_function(obj, u'slice', slice, 2)

    obj.freeze()


@complete_native_routine
def slice(routine):
    this, args = routine.method_args()
    o = this.ToObject()
    from_index = get_arg(args, 0).ToUInt32()
    to_index = get_arg(args, 1).ToUInt32()
    from obin.objects.object_space import object_space
    n = object_space.newvector(length=_w(to_index-from_index))
    index = 0
    for item in xrange(from_index, to_index):
        api.put_property(n, unicode(str(index)), o.get(unicode(str(item))))
        index += 1
    return n


# 15.4.4.7
@complete_native_routine
def push(routine):
    this, args = routine.method_args()
    o = this.ToObject()
    for item in args:
        e = item
        o._items.append(e)

    return o.length()

@complete_native_routine
def length(routine):
    this = routine.get_arg(0)
    return this.length()

# 15.4.4.5
@complete_native_routine
def join(routine):
    this, args = routine.method_args()
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
@complete_native_routine
def pop(routine):
    this, args = routine.method_args()
    o = this.ToObject()
    return o._items.pop()

@complete_native_routine
def shift(routine):
    this, args = routine.method_args()
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
@complete_native_routine
def reverse(routine):
    this, args = routine.method_args()
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


@complete_native_routine
def last_index_of(routine):
    this, args = routine.method_args()
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

    from obin.objects.object import W_Integer
    for i in xrange(from_index, -1, -1):
        y = obj.get(unicode(str(i)))
        if elem == y:
            return W_Integer(i)
    return W_Integer(-1)


@complete_native_routine
def index_of(routine):
    this, args = routine.method_args()
    obj = this
    length = this.get(u'length').ToUInt32()
    elem = get_arg(args, 0)
    from_index = get_arg(args, 1).ToUInt32()

    from obin.objects.object import W_Integer
    for i in xrange(from_index, length):
        y = obj.get(unicode(str(i)))
        if elem == y:
            return W_Integer(i)
    return W_Integer(-1)

#TODO FIX IT
@complete_native_routine
def for_each(routine):
    this, args = routine.method_args()
    obj = this
    length = this.get(u'length').value()

    callback = get_arg(args, 0)
    from obin.objects.object_space import isfunction
    assert isfunction(callback)

    for i in xrange(length):
        x = obj.get(unicode(str(i)))
        callback.Call(args=[x], this=newundefined())


# 15.4.4.11
@complete_native_routine
def sort(routine):
    this, args = routine.method_args()
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
            from obin.runtime.exception import ObinTypeError
            raise ObinTypeError(u'')

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
