from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit


def isint(w):
    from obin.objects.object import W_IntNumber
    return isinstance(w, W_IntNumber)


def isstr(w):
    from obin.objects.object import W_String
    return isinstance(w, W_String)


def isfloat(w):
    from obin.objects.object import W_FloatNumber
    return isinstance(w, W_FloatNumber)


@enforceargs(int)
def newint(i):
    from obin.objects.object import W_IntNumber
    return W_IntNumber(i)


@enforceargs(float)
def newfloat(f):
    from obin.objects.object import W_FloatNumber
    return W_FloatNumber(f)


@enforceargs(unicode)
def newstring(s):
    from obin.objects.object import W_String
    return W_String(s)


w_True = None
w_False = None

def makebools():
    global w_True
    global w_False
    from obin.objects.object import W_Boolean
    w_True = W_Boolean(True)
    w_False = W_Boolean(False)
    jit.promote(w_True)
    jit.promote(w_False)

def _makeundefined():
    from obin.objects.object import W_Undefined
    return W_Undefined()

w_Undefined = _makeundefined()
jit.promote(w_Undefined)

def _makenull():
    from obin.objects.object import W_Null
    return W_Null()

w_Null = _makenull()
jit.promote(w_Null)


def isnull(value):
    return value is w_Null


def newnull():
    return w_Null


def isundefined(value):
    return value is w_Undefined


def newundefined():
    return w_Undefined


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False


@enforceargs(bool)
def newbool(val):
    if not w_False:
        makebools()

    if val:
        return w_True
    return w_False


class ObjectSpace(object):
    def __init__(self):
        self.global_context = None
        self.global_object = None
        self.proto_function = newnull()
        self.proto_boolean = newnull()
        self.proto_number = newnull()
        self.proto_string = newnull()
        self.proto_array = newnull()
        self.proto_date = newnull()
        self.proto_object = newnull()
        self.interpreter = None

    def get_global_environment(self):
        return self.global_context.variable_environment()

    def assign_proto(self, obj, proto=None):
        from obin.objects.object import W_BasicFunction, W_String, W_Boolean, W_Number, W__Array
        if proto is not None:
            obj._prototype_ = proto
            return obj

        if isinstance(obj, W_BasicFunction):
            obj._prototype_ = self.proto_function
        elif isinstance(obj, W_Boolean):
            obj._prototype_ = self.proto_boolean
        elif isinstance(obj, W_Number):
            obj._prototype_ = self.proto_number
        elif isinstance(obj, W_String):
            obj._prototype_ = self.proto_string
        elif isinstance(obj, W__Array):
            obj._prototype_ = self.proto_array
        else:
            obj._prototype_ = self.proto_object
        return obj

    def new_obj(self):
        from obin.objects.object import W__Object
        obj = W__Object()
        self.assign_proto(obj)
        return obj

    def new_func(self, function_body, formal_parameter_list=[], scope=None):
        from obin.objects.object import W__Function
        obj = W__Function(function_body, formal_parameter_list, scope)
        self.assign_proto(obj)
        return obj

    def new_array(self, length=None):
        if not length:
            length = _w(0)
        from obin.objects.object import W__Array
        obj = W__Array()
        self.assign_proto(obj)
        return obj


object_space = ObjectSpace()

@specialize.argtype(0)
def _w(value):
    from obin.objects.object import W_Root, put_property
    if value is None:
        return newnull()
    elif isinstance(value, W_Root):
        return value
    elif isinstance(value, bool):
        return newbool(value)
    elif isinstance(value, int):
        return newint(value)
    elif isinstance(value, long):
        return newint(int(value))
    elif isinstance(value, float):
        return newfloat(value)
    elif isinstance(value, unicode):
        return newstring(value)
    elif isinstance(value, str):
        u_str = unicode(value)
        return newstring(u_str)
    elif isinstance(value, list):
        a = object_space.new_array()
        for index, item in enumerate(value):
            put_property(a, unicode(str(index)), _w(item), writable=True, enumerable=True, configurable=True)
        return a

    raise TypeError("ffffuuu %s" % (str(type(value)),))



def w_return(fn):
    def f(*args):
        return _w(fn(*args))
    return f


def hide_on_translate(*args):
    default = None

    def _wrap(f):
        def _wrapped_f(*args):
            from rpython.rlib.objectmodel import we_are_translated
            if not we_are_translated():
                return f(*args)

            return default
        return _wrapped_f

    if len(args) == 1 and callable(args[0]):
        return _wrap(args[0])
    else:
        default = args[0]
        return _wrap
