from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit
from obin.objects.types.oconstant import W_True, W_False, W_Undefined, W_Nil, W_Constant

w_True = W_True()
w_False = W_False()
w_Undefined = W_Undefined()
w_Interrupt = W_Constant()
w_Nil = W_Nil()

jit.promote(w_True)
jit.promote(w_False)
jit.promote(w_Undefined)
jit.promote(w_Nil)
jit.promote(w_Interrupt)


@enforceargs(int)
def newint(i):
    from obin.objects.types.ovalue import W_Integer
    return W_Integer(i)


@enforceargs(float)
def newfloat(f):
    from obin.objects.types.ovalue import W_Float
    return W_Float(f)


@enforceargs(str)
def newchar(c):
    from obin.objects.types.ovalue import W_Char
    return W_Char(ord(c))


@enforceargs(str)
def newstring_from_str(s):
    return newstring(unicode(s))


@enforceargs(unicode)
def newstring(s):
    from obin.objects.types.ostring import W_String
    return W_String(s)


def newinterrupt():
    return w_Interrupt


def newnil():
    return w_Nil


def newundefined():
    return w_Undefined


@enforceargs(bool)
def newbool(val):
    if val:
        return w_True
    return w_False


def newtrue():
    return w_True


def newfalse():
    return w_False


def newfunc(name, bytecode, scope):
    from obin.objects.types.ofunction import W_Function
    obj = W_Function(name, bytecode, scope)
    return obj


def newfuncsource(name, bytecode):
    from obin.objects.types.ofunction import W_FunctionSource
    obj = W_FunctionSource(name, bytecode)
    return obj


def newprimitive(name, function, arity):
    from obin.objects.types.oprimitive import W_Primitive
    obj = W_Primitive(name, function, arity)
    return obj


def newobject():
    from obin.objects.types.oobject import W_Object
    obj = W_Object(None)
    return obj


def newplainobject():
    from obin.objects.types.oobject import W_Object
    obj = W_Object(None)
    return obj


def newplainobject_with_slots(slots):
    from obin.objects.types.oobject import W_Object
    obj = W_Object(slots)
    return obj


def newvector(items):
    assert isinstance(items, list)
    from obin.objects.types.ovector import W_Vector
    obj = W_Vector(items)
    return obj


def newtuple(tupl):
    from obin.objects.types.otuple import W_Tuple
    return W_Tuple(list(tupl))


def newcoroutine(fn):
    from obin.objects.types.ocoroutine import W_Coroutine
    obj = W_Coroutine(fn)
    return obj


def newmodule(process, name, code):
    assert isstring(name)
    from obin.objects.types.omodule import W_Module
    obj = W_Module(name, code, process.builtins)
    return obj


def newgeneric(name):
    assert isstring(name)
    from obin.objects.types.dispatch.ogeneric import W_Generic
    obj = W_Generic(name)
    return obj


def newtrait(name):
    from obin.objects.types.otrait import W_Trait
    return W_Trait(name)


def newtraits(traits):
    return newvector(traits)


def isany(value):
    from obin.objects.types.oroot import W_Root
    return isinstance(value, W_Root)


def isundefined(value):
    return value is w_Undefined


def isinterrupt(value):
    return value is w_Interrupt


def iscell(value):
    from obin.objects.types.oroot import W_Cell
    return isinstance(value, W_Cell)


def isobject(value):
    from obin.objects.types.oobject import W_Object
    return isinstance(value, W_Object)


def isvaluetype(value):
    from obin.objects.types.ovalue import W_ValueType
    return isinstance(value, W_ValueType)


def isfunction(value):
    from obin.objects.types.ofunction import W_Function
    from obin.objects.types.oprimitive import W_Primitive
    return isinstance(value, W_Function) or isinstance(value, W_Primitive)


def isvector(value):
    from obin.objects.types.ovector import W_Vector
    return isinstance(value, W_Vector)


def istrait(w):
    from obin.objects.types.otrait import W_Trait
    return isinstance(w, W_Trait)


def isgeneric(w):
    from obin.objects.types.dispatch.ogeneric import W_Generic
    return isinstance(w, W_Generic)


def istuple(w):
    from obin.objects.types.otuple import W_Tuple
    return isinstance(w, W_Tuple)


def ismodule(w):
    from obin.objects.types.omodule import W_Module
    return isinstance(w, W_Module)


def isboolean(value):
    return value is w_False or value is w_True


def isnull(value):
    return value is w_Nil


def isint(w):
    from obin.objects.types.ovalue import W_Integer
    return isinstance(w, W_Integer)


def isstring(w):
    from obin.objects.types.ostring import W_String
    return isinstance(w, W_String)


def isfloat(w):
    from obin.objects.types.ovalue import W_Float
    return isinstance(w, W_Float)


def isconstant(w):
    from obin.objects.types.oconstant import W_Constant
    return isinstance(w, W_Constant)


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False


@specialize.argtype(0)
def _w(value):
    from obin.objects.types.oroot import W_Root
    if value is None:
        return newnil()
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
        return newvector(value)

    raise TypeError("ffffuuu %s" % (str(type(value)),))




class Generics:
    def __init__(self):
        self.Length = newgeneric(newstring(u"length"))
        self.Add = newgeneric(newstring(u"__add__"))
        self.Sub = newgeneric(newstring(u"__sub__"))
        self.Mul = newgeneric(newstring(u"__mul__"))
        self.Div = newgeneric(newstring(u"__div__"))
        self.Mod = newgeneric(newstring(u"__mod__"))
        self.Equal = newgeneric(newstring(u"__equal__"))
        self.Compare = newgeneric(newstring(u"__compare__"))
        self.UnaryMinus = newgeneric(newstring(u"__unary_minus__"))
        self.UnaryPlus = newgeneric(newstring(u"__unary_plus__"))
        self.BitNot = newgeneric(newstring(u"__bitnot__"))
        self.BitOr = newgeneric(newstring(u"__bitor__"))
        self.BitXor = newgeneric(newstring(u"__bitxor__"))
        self.BitAnd = newgeneric(newstring(u"__bitand__"))
        self.LeftShift = newgeneric(newstring(u"__left_shift__"))
        self.RightShift = newgeneric(newstring(u"__right_shift__"))
        self.UnsignedRightShift = newgeneric(newstring(u"__unsigned_right_shift__"))


class Traits:
    def __init__(self):
        self.Any = newtrait(newstring(u"Any"))
        self.Boolean = newtrait(newstring(u"Boolean"))

        self.True = newtrait(newstring(u"True"))
        self.TrueTraits = newtraits([self.True, self.Boolean, self.Any])

        self.False = newtrait(newstring(u"False"))
        self.FalseTraits = newtraits([self.False, self.Boolean, self.Any])

        self.Nil = newtrait(newstring(u"Nil"))
        self.NilTraits = newtraits([self.Nil, self.Any])

        self.Undefined = newtrait(newstring(u"Undefined"))
        self.UndefinedTraits = newtraits([self.Undefined, self.Any])

        self.Char = newtrait(newstring(u"Char"))
        self.CharTraits = newtraits([self.Char, self.Any])

        self.Number = newtrait(newstring(u"Number"))
        self.Integer = newtrait(newstring(u"Integer"))
        self.IntegerTraits = newtraits([self.Integer, self.Number, self.Any])

        self.Float = newtrait(newstring(u"Float"))
        self.FloatTraits = newtraits([self.Float, self.Number, self.Any])

        self.Symbol = newtrait(newstring(u"Symbol"))
        self.SymbolTraits = newtraits([self.Symbol, self.Any])

        self.String = newtrait(newstring(u"String"))
        self.StringTraits = newtraits([self.String, self.Any])

        self.List = newtrait(newstring(u"List"))

        self.Vector = newtrait(newstring(u"Vector"))
        self.VectorTraits = newtraits([self.Vector, self.Any])

        self.Tuple = newtrait(newstring(u"Tuple"))
        self.TupleTraits = newtraits([self.Tuple, self.Any])

        self.Function = newtrait(newstring(u"Function"))
        self.FunctionTraits = newtraits([self.Function, self.Any])

        self.Coroutine = newtrait(newstring(u"Coroutine"))
        self.CoroutineTraits = newtraits([self.Coroutine, self.Function, self.Any])

        self.Generic = newtrait(newstring(u"Generic"))
        self.GenericTraits = newtraits([self.Generic, self.Function, self.Any])

        self.Primitive = newtrait(newstring(u"Primitive"))
        self.PrimitiveTraits = newtraits([self.Primitive, self.Function, self.Any])

        self.Object = newtrait(newstring(u"Object"))
        self.ObjectTraits = newtraits([self.Object, self.Any])

        self.Module = newtrait(newstring(u"Object"))
        self.ModuleTraits = newtraits([self.Module, self.Any])


class StdLib:
    def __init__(self):
        self.traits = Traits()
        self.generics = Generics()


stdlib = StdLib()
