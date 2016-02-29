from obin.misc.platform import jit
from obin.types.boolean import W_True, W_False
from obin.types.nil import W_Nil
from obin.types.root import W_UniqueType

w_True = W_True()
w_False = W_False()
w_Interrupt = W_UniqueType()
w_Nil = W_Nil()

jit.promote(w_True)
jit.promote(w_False)
jit.promote(w_Nil)
jit.promote(w_Interrupt)


def isany(value):
    from obin.types.root import W_Any
    return isinstance(value, W_Any)


def isvaluetype(value):
    from obin.types.root import W_ValueType
    return isinstance(value, W_ValueType)


def isuniquetype(w):
    from obin.types.root import W_UniqueType
    return isinstance(w, W_UniqueType)


########################################################

# TODO CHECK FOR BIGINT OVERFLOW
def newint(i):
    from obin.types.integer import W_Integer
    return W_Integer(i)


def isint(w):
    from obin.types.integer import W_Integer
    return isinstance(w, W_Integer)


def newfloat(f):
    assert isinstance(f, float)
    from obin.types.floating import W_Float
    return W_Float(f)


def isfloat(w):
    from obin.types.floating import W_Float
    return isinstance(w, W_Float)


def newnumber(value):
    from obin.misc.platform import rarithmetic
    if isinstance(value, float):
        return newfloat(value)
    try:
        return newint(rarithmetic.ovfcheck(value))
    except OverflowError:
        return newfloat(float(value))


def isnumber(w):
    return isint(w) or isfloat(w)


########################################################

def newchar(c):
    assert isinstance(c, str)
    from obin.types.character import W_Char
    return W_Char(ord(c))


########################################################

def newstring_s(s):
    assert isinstance(s, str)
    return newstring(unicode(s))


def newstring(s):
    assert isinstance(s, unicode)
    from obin.types.string import W_String
    return W_String(s)


def isstring(w):
    from obin.types.string import W_String
    return isinstance(w, W_String)


########################################################

def newsymbol(process, s):
    assert isinstance(s, unicode)
    return process.symbols.symbol(s)


def newsymbol_s(process, s):
    assert isinstance(s, str)
    return process.symbols.symbol_s(s)


def newsymbol_string(process, s):
    assert isstring(s)
    return process.symbols.symbol_string(s)


def issymbol(w):
    from obin.types.symbol import W_Symbol
    return isinstance(w, W_Symbol)


########################################################

def newinterrupt():
    return w_Interrupt


def isinterrupt(value):
    return value is w_Interrupt


########################################################

def newnil():
    return w_Nil


def isnil(value):
    return value is w_Nil


########################################################

def newbool(val):
    assert isinstance(val, bool)
    if val:
        return w_True
    return w_False


def newtrue():
    return w_True


def newfalse():
    return w_False


def isboolean(value):
    return value is w_False or value is w_True


def istrue(value):
    return value is w_True


def isfalse(value):
    return value is w_False


########################################################

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


def isfunction(value):
    from obin.types.function import W_Function
    from obin.types.native_function import W_NativeFunction
    return isinstance(value, W_Function) or isinstance(value, W_NativeFunction)


def isnativefunction(value):
    from obin.types.native_function import W_NativeFunction
    return isinstance(value, W_NativeFunction)


########################################################

def newmap():
    from obin.types.map import create_empty_map
    return create_empty_map()


def ismap(value):
    from obin.types.map import W_Map
    return isinstance(value, W_Map)


########################################################

def newpmap(args):
    from obin.types.pmap import pmap
    return pmap(args)


def ispmap(value):
    from obin.types.pmap import W_PMap
    return isinstance(value, W_PMap)


########################################################

def newtvar(value):
    from obin.types.tvar import W_TVar
    return W_TVar(value)


def istvar(value):
    from obin.types.tvar import W_TVar
    return isinstance(value, W_TVar)


########################################################

def newvector(items):
    assert isinstance(items, list)
    verify_list(items)
    from obin.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def isvector(value):
    from obin.types.vector import W_Vector
    return isinstance(value, W_Vector)


########################################################

def newlist(items):
    from obin.types.plist import plist
    verify_list(items)
    return plist(items)


def islist(value):
    from obin.types.plist import W_PList
    return isinstance(value, W_PList)


def verify_list(items):
    for i in items:
        assert isany(i), i


########################################################

def newtuple(items):
    from obin.types.tupl import W_Tuple
    assert isinstance(items, list)
    verify_list(items)
    return W_Tuple(list(items))


def newunit():
    from obin.types.tupl import W_Tuple
    return W_Tuple([])


def istuple(w):
    from obin.types.tupl import W_Tuple
    return isinstance(w, W_Tuple)


#########################################################

def newscope():
    from obin.types.scope import W_Scope
    return W_Scope()


def isscope(w):
    from obin.types.scope import W_Scope
    return isinstance(w, W_Scope)


########################################################

def newenvsource(name, code):
    assert name is None or issymbol(name)
    from obin.types.environment import W_EnvSource
    obj = W_EnvSource(name, code)
    return obj


def newenv(name, scope, outer_environment):
    from obin.types.environment import W_Env
    env = W_Env(name, scope, outer_environment)
    return env


def newemptyenv(name):
    return newenv(name, newscope().finalize(None, None), None)


def isenv(w):
    from obin.types.environment import W_Env
    return isinstance(w, W_Env)


########################################################

def newgeneric(name):
    assert issymbol(name)
    from obin.types.dispatch.generic import W_Generic
    obj = W_Generic(name, None)
    return obj


def isgeneric(w):
    from obin.types.dispatch.generic import W_Generic
    return isinstance(w, W_Generic)


def newgeneric_hotpath(name, hot_path, arity):
    assert issymbol(name)
    assert hot_path is not None
    from obin.types.dispatch.generic import W_Generic
    from obin.builtins.generics.hotpath import HotPath
    obj = W_Generic(name, HotPath(hot_path, arity))
    return obj


########################################################

def newtrait(name):
    from obin.types.trait import W_Trait
    assert issymbol(name)
    return W_Trait(name, None)


def istrait(w):
    from obin.types.trait import W_Trait
    return isinstance(w, W_Trait)


########################################################

def newdatatype(name, fields, constructor):
    from obin.types.datatype import W_DataType
    assert issymbol(name)
    return W_DataType(name, fields, constructor)


def newnativedatatype(name, traits):
    datatype = newdatatype(name, newlist([]), newnil())
    datatype.add_traits(traits)
    return datatype


def newnativetypeconstructor(name, union):
    datatype = newdatatype(name, newlist([]), newnil())
    datatype.be_part_of_union(union)
    return datatype


def isdatatype(w):
    from obin.types.datatype import W_DataType
    return isinstance(w, W_DataType)


def isrecord(w):
    from obin.types.datatype import W_Record
    return isinstance(w, W_Record)


########################################################

def isoperator(w):
    from obin.compile.parse.basic import W_Operator
    return isinstance(w, W_Operator)
