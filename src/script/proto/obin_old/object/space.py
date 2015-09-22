from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit

@enforceargs(int)
def newint(i):
    from obj import W_IntNumber

    return W_IntNumber(i)


@enforceargs(float)
def newfloat(f):
    from obj import W_FloatNumber

    return W_FloatNumber(f)


@enforceargs(unicode)
def newstring(s):
    from obj import W_String

    return W_String(s)


def _makeundefined():
    from obj import W_Undefined
    return W_Undefined()

w_Undefined = _makeundefined()
jit.promote(w_Undefined)


def _makenull():
    from obj import W_Null
    return W_Null()

w_Null = _makenull()
jit.promote(w_Null)


@enforceargs(bool)
def _makebool(b):
    from obj import W_Boolean

    return W_Boolean(b)


w_True = _makebool(True)
jit.promote(w_True)

w_False = _makebool(False)
jit.promote(w_False)

@enforceargs(bool)
def newbool(val):
    if val:
        return w_True
    return w_False

def newnull():
    return w_Null

def newundefined():
    return w_Undefined

def newobject():
    from obj import W_Object
    obj = W_Object()
    return obj

def newfunc(function_body, formal_parameter_list=[], scope=None):
    from obj import W_Function
    obj = W_Function(function_body, formal_parameter_list, scope)
    return obj

def newdate(value):
    from obj import W_Date
    obj = W_Date(value)
    return obj

def newstring(value):
    from obj import W_String
    obj = W_String(value)
    return obj

def newnumber(value):
    from obj import W_FloatNumber
    obj = W_FloatNumber(value)
    return obj

@specialize.argtype(0)
def _w(value):
    from obj import W_Root, put_property

    if value is None:
        return newnull()
    elif isinstance(value, W_Root):
        return value
    elif isinstance(value, bool):
        return newbool(value)
    elif isinstance(value, int):
        return newint(value)
    elif isinstance(value, float):
        return newfloat(value)
    elif isinstance(value, unicode):
        return newstring(value)
    elif isinstance(value, str):
        u_str = unicode(value)
        return newstring(u_str)
    elif isinstance(value, list):
        a = newobject()
        for index, item in enumerate(value):
            put_property(a, unicode(str(index)), _w(item), writable=True, enumerable=True, configurable=True)
        return a

    raise TypeError("ffffuuu %s" % (value,))


def isnull(val):
    return val is w_Null


def isundefined(val):
    return val is w_Undefined


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False

def isint(w):
    from obj import W_IntNumber

    return isinstance(w, W_IntNumber)


def isstr(w):
    from obj import W_String

    return isinstance(w, W_String)


def isfloat(w):
    from obj import W_FloatNumber

    return isinstance(w, W_FloatNumber)

def isfunc(w):
    from obj import W_BasicFunction

    return isinstance(w, W_BasicFunction)


class ObjectSpace(object):
    def __init__(self):
        self.global_context = None
        self.global_object = None
        self.function_traits = newnull()
        self.boolean_traits = newnull()
        self.number_traits = newnull()
        self.string_traits = newnull()
        self.proto_date = newnull()
        self.proto_object = newnull()
        self.vector_traits = newnull()
        self.interpreter = None

    def get_global_environment(self):
        return self.global_context.variable_environment()


object_space = ObjectSpace()


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
