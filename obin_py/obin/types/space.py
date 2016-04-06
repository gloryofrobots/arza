from obin.misc.platform import jit
from obin.types.boolean import W_True, W_False
from obin.types.void import W_Void
from obin.types.root import W_UniqueType

w_True = W_True()
w_False = W_False()
w_Interrupt = W_UniqueType()
w_Void = W_Void()

jit.promote(w_True)
jit.promote(w_False)
jit.promote(w_Void)
jit.promote(w_Interrupt)


def isany(value):
    from obin.types.root import W_Root
    return isinstance(value, W_Root)


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

def newvoid():
    return w_Void


def isvoid(value):
    return value is w_Void


########################################################

def newbool(val):
    assert isinstance(val, bool)
    if val:
        return w_True
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
    from obin.types.partial import W_Partial
    from obin.types.method import W_Method
    return isinstance(value, W_Function) or isinstance(value, W_NativeFunction) \
           or isinstance(value, W_Partial) or isinstance(value, W_Method)


def isnativefunction(value):
    from obin.types.native_function import W_NativeFunction
    return isinstance(value, W_NativeFunction)


########################################################

def newpartial(func):
    from obin.types.partial import newpartial
    return newpartial(func)


def ispartial(w):
    from obin.types.partial import W_Partial
    return isinstance(w, W_Partial)


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
    verify_list_DEBUG(items)
    from obin.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def isvector(value):
    from obin.types.vector import W_Vector
    return isinstance(value, W_Vector)

########################################################

def newpvector(items):
    assert isinstance(items, list)
    verify_list_DEBUG(items)
    from obin.types.pvector import newpvector
    obj = newpvector(items)
    return obj


def ispvector(value):
    from obin.types.pvector import W_PVector
    return isinstance(value, W_PVector)


########################################################

def newlist(items):
    from obin.types.plist import plist
    verify_list_DEBUG(items)
    return plist(items)


def islist(value):
    from obin.types.plist import W_PList
    return isinstance(value, W_PList)


def verify_list_DEBUG(items):
    for i in items:
        assert isany(i), i


########################################################

def newtuple(items):
    from obin.types.tuples import W_Tuple
    assert isinstance(items, list)
    if len(items) == 0:
        return newunit()

    verify_list_DEBUG(items)
    return W_Tuple(items)


def newunit():
    from obin.types.tuples import W_Unit
    return W_Unit()


def isunit(w):
    from obin.types.tuples import W_Unit
    return isinstance(w, W_Unit)


def istuple(w):
    from obin.types.tuples import W_Tuple, W_Unit
    return isinstance(w, W_Tuple) or isinstance(w, W_Unit)


def isrealtuple(w):
    from obin.types.tuples import W_Tuple
    return isinstance(w, W_Tuple)


#########################################################
def newarguments(stack, index, length):
    from obin.types.arguments import W_Arguments
    return W_Arguments(stack, index, length)


def isarguments(w):
    from obin.types.arguments import W_Arguments
    return isinstance(w, W_Arguments)


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

def newmethod(name, trait, signature):
    from obin.types.method import method
    assert issymbol(name)
    assert istrait(trait)
    assert islist(signature)

    obj = method(name, trait, signature, newvoid())
    return obj


def newmethod_default_implementation(name, trait, signature, default):
    from obin.types.method import method
    assert issymbol(name)
    assert istrait(trait)
    assert islist(signature)
    assert isfunction(default) or isvoid(default)
    obj = method(name, trait, signature, default)
    return obj


def ismethod(w):
    from obin.types.method import W_Method
    return isinstance(w, W_Method)


def newmethod_hotpath(name, trait, signature, hot_path):
    assert issymbol(name)
    assert istrait(trait)
    assert islist(signature)

    assert hot_path is not None
    from obin.types.method import method_with_hotpath
    obj = method_with_hotpath(name, trait, signature, newvoid(), hot_path)
    return obj


########################################################

def newtrait(name, varname, constraints):
    from obin.types.trait import W_Trait
    from obin.runtime import error
    error.affirm_type(name, issymbol)
    error.affirm_type(varname, issymbol)
    error.affirm_type(constraints, islist)
    error.affirm_iterable(constraints, istrait)

    return W_Trait(name, varname, constraints)


def istrait(w):
    from obin.types.trait import W_Trait
    return isinstance(w, W_Trait)


########################################################

def newdatatype(name, fields, constructor):
    from obin.types.datatype import W_DataType
    assert issymbol(name)
    return W_DataType(name, fields, constructor)


def newunion(name, types):
    from obin.types.datatype import W_Union
    assert issymbol(name)
    assert islist(types)

    return W_Union(name, types)


def newnativedatatype(name):
    datatype = newdatatype(name, newlist([]), newvoid())
    return datatype


def isdatatype(w):
    from obin.types.datatype import W_DataType
    return isinstance(w, W_DataType)


def isunion(w):
    from obin.types.datatype import W_Union
    return isinstance(w, W_Union)


def isrecord(w):
    from obin.types.datatype import W_Record
    return isinstance(w, W_Record)


########################################################

def isoperator(w):
    from obin.compile.parse.basic import W_Operator
    return isinstance(w, W_Operator)


############################################################

def safe_w(obj):
    if not isany(obj):
        s = "<PyObj type:%s, repr:%s>" % (type(obj), repr(obj))
        return newstring_s(s)
    return obj
