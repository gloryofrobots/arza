from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit


@enforceargs(int)
def newint(i):
    from obin.objects.object import W_Integer
    return W_Integer(i)


@enforceargs(float)
def newfloat(f):
    from obin.objects.object import W_Float
    return W_Float(f)


@enforceargs(str)
def newchar(c):
    from obin.objects.object import W_Char
    return W_Char(ord(c))


def newstring(s):
    from obin.objects.object import W_String
    return W_String(unicode(s))


w_True = None
w_False = None


def makebools():
    global w_True
    global w_False
    from obin.objects.object import W_True, W_False
    w_True = W_True()
    w_False = W_False()
    jit.promote(w_True)
    jit.promote(w_False)


def _makeundefined():
    from obin.objects.object import W_Undefined
    return W_Undefined()


w_Undefined = _makeundefined()
jit.promote(w_Undefined)


def _makenull():
    from obin.objects.object import W_Nil
    return W_Nil()


w_Null = _makenull()
jit.promote(w_Null)


def newnull():
    return w_Null


def newundefined():
    return w_Undefined


@enforceargs(bool)
def newbool(val):
    if not w_False:
        makebools()

    if val:
        return w_True
    return w_False


def newfunc(function_body, params, scope):
    from obin.objects.object import W_Function
    obj = W_Function(function_body, params, scope)
    return obj


def newsimpleobject():
    from obin.objects.object import W_Object
    obj = W_Object(None)
    return obj

def newsimpleobject_withsize(size):
    from obin.objects.object import W_Object
    from obin.objects.datastructs import Slots
    slots = Slots(size)
    obj = W_Object(slots)
    return obj

def newobject():
    obj = newsimpleobject()
    obj.create_traits(None)
    obj.isa(object_space.traits.Object)
    return obj
def newvector(items=None):
    from obin.objects.object import W_Vector
    obj = W_Vector(items)
    return obj


def isundefined(value):
    return value is w_Undefined


def iscell(value):
    from object import W_Cell
    return isinstance(value, W_Cell)


def isobject(value):
    from object import W_Object
    return isinstance(value, W_Object)


def isprimitive(value):
    from object import W_Primitive
    return isinstance(value, W_Primitive)


def isfunction(value):
    from object import W_Function
    return isinstance(value, W_Function)


def isvector(value):
    from object import W_Vector
    return isinstance(value, W_Vector)


def isnull(value):
    return value is w_Null


def isint(w):
    from obin.objects.object import W_Integer
    return isinstance(w, W_Integer)


def isstring(w):
    from obin.objects.object import W_String
    return isinstance(w, W_String)


def isfloat(w):
    from obin.objects.object import W_Float
    return isinstance(w, W_Float)


def isconstant(w):
    from obin.objects.object import W_Constant
    return isinstance(w, W_Constant)


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False




class ObjectSpace(object):
    class Traits(object):
        def __init__(self):
            self.Object = None
            self.Function = None
            self.True = None
            self.False = None
            self.Nil = None
            self.Undefined = None

            self.Char = None
            self.Integer = None
            self.Float = None
            self.Symbol = None

            self.String = None
            self.Array = None
            self.List = None
            self.Vector = None
            self.Tuple = None

    def __init__(self):
        self.global_context = None
        self.global_object = None

        self.traits = ObjectSpace.Traits()
        self.init_traits()
        self.interpreter = None

    def newobject(self):
        obj = newsimpleobject()
        obj.create_traits(None)
        obj.isa(self.traits.Object)
        return obj

    def init_traits(self):
        self.traits.Object = newsimpleobject()
        self.traits.Object.create_traits(None)

        # following traits resemble native types list
        self.traits.Function = self.newobject()
        self.traits.True = self.newobject()
        self.traits.False = self.newobject()
        self.traits.Nil = self.newobject()
        self.traits.Undefined = self.newobject()

        self.traits.Char = self.newobject()
        self.traits.Integer = self.newobject()
        self.traits.Float = self.newobject()
        self.traits.Symbol = self.newobject()

        self.traits.String = self.newobject()
        self.traits.Array = self.newobject()
        self.traits.List = self.newobject()
        self.traits.Vector = self.newobject()
        self.traits.Tuple = self.newobject()

    def get_global_environment(self):
        return self.global_context.env()


object_space = ObjectSpace()


@specialize.argtype(0)
def _w(value):
    from obin.objects.object import W_Root
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
        return newvector(value)

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
