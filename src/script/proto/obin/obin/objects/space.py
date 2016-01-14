from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit
from obin.objects.types.boolean import W_True, W_False
from obin.objects.types.nil import W_Nil
from obin.objects.types.undefined import W_Undefined
from obin.objects.types.root import W_Constant

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


# TODO CHECK FOR BIGINT OVERFLOW
@enforceargs(int)
def newint(i):
    from obin.objects.types.integer import W_Integer
    return W_Integer(i)


@enforceargs(float)
def newfloat(f):
    from obin.objects.types.floating import W_Float
    return W_Float(f)


@specialize.argtype(0)
def newnumber(value):
    if isinstance(value, int):
        return newint(value)
    elif isinstance(value, float):
        return newfloat(value)

    assert False, "invalid number type"


@enforceargs(str)
def newchar(c):
    from obin.objects.types.character import W_Char
    return W_Char(ord(c))


@enforceargs(str)
def newstring_from_str(s):
    return newstring(unicode(s))


@enforceargs(unicode)
def newstring(s):
    from obin.objects.types.string import W_String
    return W_String(s)


def newsymbol(s, idx):
    from obin.objects.types.symbol import W_Symbol
    assert isstring(s)
    return W_Symbol(s, idx)


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
    from obin.objects.types.function import W_Function
    obj = W_Function(name, bytecode, scope)
    return obj


def newfuncsource(name, bytecode):
    from obin.objects.types.function import W_FunctionSource
    obj = W_FunctionSource(name, bytecode)
    return obj


def newnativefunc(name, function, arity):
    from obin.objects.types.native_function import W_NativeFunction
    obj = W_NativeFunction(name, function, arity)
    return obj


def neworigin(function):
    from obin.objects.types.origin import W_Origin
    obj = W_Origin(function)
    return obj


def newentity(process, source, traits):
    from obin.objects.types import behavior
    from obin.objects.types.entity import W_Entity
    from obin.objects.types.plist import concat
    assert islist(traits)
    source_traits = behavior.traits(process, source)
    behavior_traits = concat(traits, source_traits)
    behavior = newbehavior(behavior_traits)
    return W_Entity(behavior, source)


def newmap():
    from obin.objects.types.map import create_empty_map
    return create_empty_map()


def newvector(items):
    assert isinstance(items, list)
    from obin.objects.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def newlist(items):
    from obin.objects.types.plist import plist
    return plist(items)


def newemptyvector():
    return newvector([])


def newtuple(tupl):
    from obin.objects.types.tupl import W_Tuple
    return W_Tuple(list(tupl))


def newmodule(process, name, code):
    assert isstring(name)
    from obin.objects.types.module import W_Module
    obj = W_Module(name, code, process.builtins)
    return obj


def newgeneric(name):
    assert isstring(name)
    from obin.objects.types.dispatch.generic import W_Generic
    obj = W_Generic(name)
    return obj


def newtrait(name):
    from obin.objects.types.trait import W_Trait
    return W_Trait(name)


def newbehavior(traits):
    assert islist(traits)
    from obin.objects.types.behavior import W_Behavior
    return W_Behavior(traits)


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


def isentity(value):
    from obin.objects.types.entity import W_Entity
    return isinstance(value, W_Entity)


def isorigin(value):
    from obin.objects.types.origin import W_Origin
    return isinstance(value, W_Origin)


def ismap(value):
    from obin.objects.types.map import W_Map
    return isinstance(value, W_Map)


def isvaluetype(value):
    from obin.objects.types.root import W_ValueType
    return isinstance(value, W_ValueType)


def isfunction(value):
    from obin.objects.types.function import W_Function
    from obin.objects.types.native_function import W_NativeFunction
    return isinstance(value, W_Function) or isinstance(value, W_NativeFunction)


def isvector(value):
    from obin.objects.types.vector import W_Vector
    return isinstance(value, W_Vector)


def islist(value):
    from obin.objects.types.plist import W_PList
    return isinstance(value, W_PList)


def istrait(w):
    from obin.objects.types.trait import W_Trait
    return isinstance(w, W_Trait)


def isbehavior(w):
    from obin.objects.types.behavior import W_Behavior
    return isinstance(w, W_Behavior)


def isgeneric(w):
    from obin.objects.types.dispatch.generic import W_Generic
    return isinstance(w, W_Generic)


def istuple(w):
    from obin.objects.types.tupl import W_Tuple
    return isinstance(w, W_Tuple)


def ismodule(w):
    from obin.objects.types.module import W_Module
    return isinstance(w, W_Module)


def isboolean(value):
    return value is w_False or value is w_True


def istrue(value):
    return value is w_True


def isfalse(value):
    return value is w_False


def isnull(value):
    return value is w_Nil


def isstring(w):
    from obin.objects.types.string import W_String
    return isinstance(w, W_String)


def isint(w):
    from obin.objects.types.integer import W_Integer
    return isinstance(w, W_Integer)


def isfloat(w):
    from obin.objects.types.floating import W_Float
    return isinstance(w, W_Float)


def isnumber(w):
    return isint(w) or isfloat(w)


def isconstant(w):
    from obin.objects.types.root import W_Constant
    return isinstance(w, W_Constant)


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False
