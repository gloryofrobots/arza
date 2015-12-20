from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit


@enforceargs(int)
def newint(i):
    from obin.objects.types.value import W_Integer
    return W_Integer(i)


@enforceargs(float)
def newfloat(f):
    from obin.objects.types.value import W_Float
    return W_Float(f)


@enforceargs(str)
def newchar(c):
    from obin.objects.types.value import W_Char
    return W_Char(ord(c))


def newstring(s):
    from obin.objects.types.value import W_String
    assert not isstring(s)
    return W_String(unicode(s))


w_True = None
w_False = None


def makebools():
    global w_True
    global w_False
    from obin.objects.types.constant import W_True, W_False
    w_True = W_True()
    w_False = W_False()
    jit.promote(w_True)
    jit.promote(w_False)


def _makeundefined():
    from obin.objects.types.constant import W_Undefined
    return W_Undefined()


w_Undefined = _makeundefined()
jit.promote(w_Undefined)


def _makenull():
    from obin.objects.types.constant import W_Nil
    return W_Nil()


w_Null = _makenull()
jit.promote(w_Null)


def _make_interrupt():
    from obin.objects.types.constant import W_Constant
    return W_Constant()


w_Interrupt = _make_interrupt()


def newinterrupt():
    return w_Interrupt


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


def newfunc(name, bytecode, scope):
    from obin.objects.types.callable import W_Function
    obj = W_Function(name, bytecode, scope)
    return obj


def newprimitive(name, function, arity):
    from obin.objects.types.callable import W_Primitive
    obj = W_Primitive(name, function, arity)
    return obj


def newobject():
    from obin.objects.types.object import W_Object
    from obin.objects import api
    obj = W_Object(None)

    obj.set_traits(api.clone(state.traits.ObjectTraits))
    return obj


def newplainobject():
    from obin.objects.types.object import W_Object
    from obin.objects import api
    obj = W_Object(None)
    return obj


def newplainobject_with_slots(slots):
    from obin.objects.types.object import W_Object
    obj = W_Object(slots)
    return obj


def newvector(items):
    from obin.objects.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def newtuple(tupl):
    from obin.objects.types.tupletype import W_Tuple
    return W_Tuple(tupl)


def newcoroutine(fn):
    from obin.objects.types.callable import W_Coroutine
    obj = W_Coroutine(fn)
    return obj


def newmodule(name, code):
    assert isstring(name)
    from obin.objects.types.module import W_Module
    obj = W_Module(name, code)
    return obj


def newgeneric(name):
    assert isstring(name)
    from obin.objects.types.dispatch.generic import W_Generic
    obj = W_Generic(name)
    return obj


def newtrait(name):
    from obin.objects.types.trait import W_Trait
    return W_Trait(name)


def newtraits(traits):
    return newvector(traits)


def isany(value):
    from obin.objects.types.root import W_Root
    return isinstance(value, W_Root)


def isundefined(value):
    return value is w_Undefined


def isinterrupt(value):
    return value is w_Interrupt


def iscell(value):
    from obin.objects.types.root import W_Cell
    return isinstance(value, W_Cell)


def isobject(value):
    from obin.objects.types.object import W_Object
    return isinstance(value, W_Object)


def isvaluetype(value):
    from obin.objects.types.value import W_ValueType
    return isinstance(value, W_ValueType)


def isfunction(value):
    from obin.objects.types.callable import W_Function, W_Primitive
    return isinstance(value, W_Function) or isinstance(value, W_Primitive)


def isvector(value):
    from obin.objects.types.vector import W_Vector
    return isinstance(value, W_Vector)


def istrait(w):
    from obin.objects.types.trait import W_Trait
    return isinstance(w, W_Trait)


def isgeneric(w):
    from obin.objects.types.dispatch.generic import W_Generic
    return isinstance(w, W_Generic)


def istuple(w):
    from obin.objects.types.tupletype import W_Tuple
    return isinstance(w, W_Tuple)


def ismodule(w):
    from obin.objects.types.module import W_Module
    return isinstance(w, W_Module)


def isboolean(value):
    return value is w_False or value is w_True


def isnull(value):
    return value is w_Null


def isint(w):
    from obin.objects.types.value import W_Integer
    return isinstance(w, W_Integer)


def isstring(w):
    from obin.objects.types.value import W_String
    return isinstance(w, W_String)


def isfloat(w):
    from obin.objects.types.value import W_Float
    return isinstance(w, W_Float)


def isconstant(w):
    from obin.objects.types.constant import W_Constant
    return isinstance(w, W_Constant)


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False


class State(object):
    class Traits(object):
        def __init__(self):
            self.Any = newtrait(newstring("Any"))
            self.Boolean = newtrait(newstring("Boolean"))

            self.True = newtrait(newstring("True"))
            self.TrueTraits = newtraits([self.True, self.Boolean, self.Any])

            self.False = newtrait(newstring("False"))
            self.FalseTraits = newtraits([self.False, self.Boolean, self.Any])

            self.Nil = newtrait(newstring("Nil"))
            self.NilTraits = newtraits([self.Nil, self.Any])

            self.Undefined = newtrait(newstring("Undefined"))
            self.UndefinedTraits = newtraits([self.Undefined, self.Any])

            self.Char = newtrait(newstring("Char"))
            self.CharTraits = newtraits([self.Char, self.Any])

            self.Number = newtrait(newstring("Number"))
            self.Integer = newtrait(newstring("Integer"))
            self.IntegerTraits = newtraits([self.Integer, self.Number, self.Any])

            self.Float = newtrait(newstring("Float"))
            self.FloatTraits = newtraits([self.Float, self.Number, self.Any])

            self.Symbol = newtrait(newstring("Symbol"))
            self.SymbolTraits = newtraits([self.Symbol, self.Any])

            self.String = newtrait(newstring("String"))
            self.StringTraits = newtraits([self.String, self.Any])

            self.List = newtrait(newstring("List"))

            self.Vector = newtrait(newstring("Vector"))
            self.VectorTraits = newtraits([self.Vector, self.Any])

            self.Tuple = newtrait(newstring("Tuple"))
            self.TupleTraits = newtraits([self.Tuple, self.Any])

            self.Function = newtrait(newstring("Function"))
            self.FunctionTraits = newtraits([self.Function, self.Any])

            self.Generic = newtrait(newstring("Generic"))
            self.GenericTraits = newtraits([self.Generic, self.Any])

            self.Primitive = newtrait(newstring("Primitive"))
            self.PrimitiveTraits = newtraits([self.Primitive, self.Any])

            self.Object = newtrait(newstring("Object"))
            self.ObjectTraits = newtraits([self.Object, self.Any])

            self.Module = newtrait(newstring("Object"))
            self.ModuleTraits = newtraits([self.Module, self.Any])

    def __init__(self):
        self.traits = State.Traits()
        self.process = None


state = State()


def newprocess(libdirs):
    from obin.builtins import setup_builtins
    from obin.runtime.process import Process
    process = Process()
    for path in libdirs:
        process.add_path(path)
    state.process = process
    setup_builtins(process.builtins)
    return process


@specialize.argtype(0)
def _w(value):
    from obin.objects.types.root import W_Root
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
