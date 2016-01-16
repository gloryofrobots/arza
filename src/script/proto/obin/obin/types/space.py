from rpython.rlib.objectmodel import specialize, enforceargs
from rpython.rlib import jit
from obin.types.boolean import W_True, W_False
from obin.types.nil import W_Nil
from obin.types.undefined import W_Undefined
from obin.types.root import W_UniqueType

w_True = W_True()
w_False = W_False()
w_Undefined = W_Undefined()
w_Interrupt = W_UniqueType()
w_Nil = W_Nil()

jit.promote(w_True)
jit.promote(w_False)
jit.promote(w_Undefined)
jit.promote(w_Nil)
jit.promote(w_Interrupt)


# TODO CHECK FOR BIGINT OVERFLOW
@enforceargs(int)
def newint(i):
    from obin.types.integer import W_Integer
    return W_Integer(i)


@enforceargs(float)
def newfloat(f):
    from obin.types.floating import W_Float
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
    from obin.types.character import W_Char
    return W_Char(ord(c))


@enforceargs(str)
def newstring_from_str(s):
    return newstring(unicode(s))


@enforceargs(unicode)
def newstring(s):
    from obin.types.string import W_String
    return W_String(s)


def newsymbol(process, s):
    assert isinstance(s, unicode)
    return process.symbols.symbol(s)


def newsymbol_py_str(process, s):
    assert isinstance(s, str)
    return newsymbol(process, unicode(s))


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
    from obin.types.function import W_Function
    assert issymbol(name)
    obj = W_Function(name, bytecode, scope)
    return obj


def newfuncsource(name, bytecode):
    from obin.types.function import W_FunctionSource
    assert issymbol(name)
    obj = W_FunctionSource(name, bytecode)
    return obj


def newnativefunc(name, function, arity):
    from obin.types.native_function import W_NativeFunction
    assert issymbol(name)
    obj = W_NativeFunction(name, function, arity)
    return obj


def neworigin(function):
    from obin.types.origin import W_Origin
    obj = W_Origin(function)
    return obj


def newentity(process, source, traits):
    from obin.types import behavior
    from obin.types.entity import W_Entity
    from obin.types.plist import concat
    assert islist(traits)
    source_traits = behavior.traits(process, source)
    behavior_traits = concat(traits, source_traits)
    behavior = newbehavior(behavior_traits)
    return W_Entity(behavior, source)


def newmap():
    from obin.types.map import create_empty_map
    return create_empty_map()


def newvector(items):
    assert isinstance(items, list)
    from obin.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def newlist(items):
    from obin.types.plist import plist
    return plist(items)


def newtuple(tupl):
    from obin.types.tupl import W_Tuple
    return W_Tuple(list(tupl))


def newmodule(process, name, code):
    assert issymbol(name)
    from obin.types.module import W_Module
    obj = W_Module(name, code, process.builtins)
    return obj


def newgeneric(name):
    assert issymbol(name)
    from obin.types.dispatch.generic import W_Generic
    obj = W_Generic(name)
    return obj


def newtrait(name):
    from obin.types.trait import W_Trait
    assert issymbol(name)
    return W_Trait(name)


def newbehavior(traits):
    assert islist(traits)
    from obin.types.behavior import W_Behavior
    return W_Behavior(traits)


def isany(value):
    from obin.types.root import W_Any
    return isinstance(value, W_Any)


def isundefined(value):
    return value is w_Undefined


def isinterrupt(value):
    return value is w_Interrupt


def iscell(value):
    from obin.types.root import W_Cell
    return isinstance(value, W_Cell)


def isentity(value):
    from obin.types.entity import W_Entity
    return isinstance(value, W_Entity)


def isorigin(value):
    from obin.types.origin import W_Origin
    return isinstance(value, W_Origin)


def ismap(value):
    from obin.types.map import W_Map
    return isinstance(value, W_Map)


def isvaluetype(value):
    from obin.types.root import W_ValueType
    return isinstance(value, W_ValueType)


def isfunction(value):
    from obin.types.function import W_Function
    from obin.types.native_function import W_NativeFunction
    return isinstance(value, W_Function) or isinstance(value, W_NativeFunction)

def isnativefunction(value):
    from obin.types.native_function import W_NativeFunction
    return isinstance(value, W_NativeFunction)

def isvector(value):
    from obin.types.vector import W_Vector
    return isinstance(value, W_Vector)


def islist(value):
    from obin.types.plist import W_PList
    return isinstance(value, W_PList)


def istrait(w):
    from obin.types.trait import W_Trait
    return isinstance(w, W_Trait)


def isbehavior(w):
    from obin.types.behavior import W_Behavior
    return isinstance(w, W_Behavior)


def isgeneric(w):
    from obin.types.dispatch.generic import W_Generic
    return isinstance(w, W_Generic)


def istuple(w):
    from obin.types.tupl import W_Tuple
    return isinstance(w, W_Tuple)


def ismodule(w):
    from obin.types.module import W_Module
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
    from obin.types.string import W_String
    return isinstance(w, W_String)


def issymbol(w):
    from obin.types.symbol import W_Symbol
    return isinstance(w, W_Symbol)


def isint(w):
    from obin.types.integer import W_Integer
    return isinstance(w, W_Integer)


def isfloat(w):
    from obin.types.floating import W_Float
    return isinstance(w, W_Float)


def isnumber(w):
    return isint(w) or isfloat(w)


def isuniquetype(w):
    from obin.types.root import W_UniqueType
    return isinstance(w, W_UniqueType)


def isnull_or_undefined(obj):
    if isnull(obj) or isundefined(obj):
        return True
    return False
