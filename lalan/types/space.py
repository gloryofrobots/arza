from lalan.misc.platform import jit
from lalan.types.boolean import W_True, W_False
from lalan.types.void import W_Void
from lalan.types.root import W_UniqueType

w_True = W_True()
w_False = W_False()
w_Interrupt = W_UniqueType()
w_Void = W_Void()

jit.promote(w_True)
jit.promote(w_False)
jit.promote(w_Void)
jit.promote(w_Interrupt)


def isany(value):
    from lalan.types.root import W_Root
    return isinstance(value, W_Root)


def isatomictype(value):
    return isvaluetype(value) or isstring(value)


def isvaluetype(value):
    from lalan.types.root import W_ValueType
    return isinstance(value, W_ValueType)


def isuniquetype(w):
    from lalan.types.root import W_UniqueType
    return isinstance(w, W_UniqueType)


########################################################

# TODO CHECK FOR BIGINT OVERFLOW
def newint(i):
    from lalan.types.integer import W_Integer
    return W_Integer(i)


def isint(w):
    from lalan.types.integer import W_Integer
    return isinstance(w, W_Integer)


def newfloat(f):
    assert isinstance(f, float)
    from lalan.types.floating import W_Float
    return W_Float(f)


def isfloat(w):
    from lalan.types.floating import W_Float
    return isinstance(w, W_Float)


def newnumber(value):
    from lalan.misc.platform import rarithmetic
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
    assert isinstance(c, unicode)
    from lalan.types.character import W_Char
    return W_Char(ord(c))


def ischar(w):
    from lalan.types.character import W_Char
    return isinstance(w, W_Char)


########################################################

def newstring_s(s):
    assert isinstance(s, str)
    return newstring(unicode(s))


def newstring(s):
    assert isinstance(s, unicode)
    from lalan.types.string import W_String
    return W_String(s)


def isstring(w):
    from lalan.types.string import W_String
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
    from lalan.types.symbol import W_Symbol
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
    from lalan.types.function import W_Function
    assert issymbol(name)
    obj = W_Function(name, bytecode, scope)
    return obj


def newfuncsource(name, bytecode):
    from lalan.types.function import W_FunctionSource
    assert issymbol(name)
    obj = W_FunctionSource(name, bytecode)
    return obj


def newnativefunc(name, function, arity):
    from lalan.types.native_function import W_NativeFunction
    assert issymbol(name)
    obj = W_NativeFunction(name, function, arity)
    return obj


def isfunction(value):
    from lalan.types.function import W_Function
    from lalan.types.native_function import W_NativeFunction
    from lalan.types.partial import W_Partial
    from lalan.types.dispatch.generic import W_Generic
    return isinstance(value, W_Function) or isinstance(value, W_NativeFunction) \
           or isinstance(value, W_Partial) or isinstance(value, W_Generic)


def isnativefunction(value):
    from lalan.types.native_function import W_NativeFunction
    return isinstance(value, W_NativeFunction)


########################################################

def newpartial(func):
    from lalan.types.partial import newpartial
    return newpartial(func)


def ispartial(w):
    from lalan.types.partial import W_Partial
    return isinstance(w, W_Partial)


########################################################

def newlazyval(func):
    from lalan.types.lazyval import W_LazyVal
    return W_LazyVal(func)


def islazyval(w):
    from lalan.types.lazyval import W_LazyVal
    return isinstance(w, W_LazyVal)


########################################################


def newiodevice(_file):
    from lalan.types.iodevice import W_IODevice
    return W_IODevice(_file)


def isiodevice(w):
    from lalan.types.iodevice import W_IODevice
    return isinstance(w, W_IODevice)


########################################################


def newmap():
    from lalan.types.map import create_empty_map
    return create_empty_map()


def ismap(value):
    from lalan.types.map import W_Map
    return isinstance(value, W_Map)


########################################################

def newpmap(args):
    from lalan.types.pmap import pmap
    return pmap(args)


def ispmap(value):
    from lalan.types.pmap import W_PMap
    return isinstance(value, W_PMap)


########################################################

def newtvar(value):
    from lalan.types.tvar import W_TVar
    return W_TVar(value)


def istvar(value):
    from lalan.types.tvar import W_TVar
    return isinstance(value, W_TVar)


########################################################

def newvector(items):
    assert isinstance(items, list)
    verify_list_DEBUG(items)
    from lalan.types.vector import W_Vector
    obj = W_Vector(items)
    return obj


def isvector(value):
    from lalan.types.vector import W_Vector
    return isinstance(value, W_Vector)


########################################################

def newpvector(items):
    assert isinstance(items, list)
    verify_list_DEBUG(items)
    from lalan.types.pvector import newpvector
    obj = newpvector(items)
    return obj


def ispvector(value):
    from lalan.types.pvector import W_PVector
    return isinstance(value, W_PVector)


########################################################

def newlist(items):
    from lalan.types.plist import plist
    verify_list_DEBUG(items)
    return plist(items)


def islist(value):
    from lalan.types.plist import W_PList
    return isinstance(value, W_PList)


def verify_list_DEBUG(items):
    for i in items:
        assert isany(i), i


########################################################

def newtuple(items):
    from lalan.types.tuples import W_Tuple
    assert isinstance(items, list)
    if len(items) == 0:
        return newunit()

    verify_list_DEBUG(items)
    return W_Tuple(items)


def newunit():
    from lalan.types.tuples import W_Unit
    return W_Unit()


def newtupleunit():
    return newtuple([newunit()])


def isunit(w):
    from lalan.types.tuples import W_Unit
    return isinstance(w, W_Unit)


def istuple(w):
    from lalan.types.tuples import W_Tuple, W_Unit
    return isinstance(w, W_Tuple) or isinstance(w, W_Unit)


def isrealtuple(w):
    from lalan.types.tuples import W_Tuple
    return isinstance(w, W_Tuple)


#########################################################
def newarguments(stack, index, length):
    from lalan.types.arguments import W_Arguments
    return W_Arguments(stack, index, length)


def isarguments(w):
    from lalan.types.arguments import W_Arguments
    return isinstance(w, W_Arguments)


#########################################################

def newscope():
    from lalan.types.scope import W_Scope
    return W_Scope()


def isscope(w):
    from lalan.types.scope import W_Scope
    return isinstance(w, W_Scope)


########################################################

def newenvsource(name, code):
    assert name is None or issymbol(name)
    from lalan.types.environment import W_EnvSource
    obj = W_EnvSource(name, code)
    return obj


def newenv(name, scope, outer_environment):
    from lalan.types.environment import W_Env
    env = W_Env(name, scope, outer_environment)
    return env


def newemptyenv(name):
    return newenv(name, newscope().finalize(None, None), None)


def isenv(w):
    from lalan.types.environment import W_Env
    return isinstance(w, W_Env)


########################################################

def newgeneric(name, signature):
    from lalan.types.dispatch.generic import generic
    assert issymbol(name)
    if not islist(signature):
        assert islist(signature)

    assert islist(signature), name

    return generic(name, signature)


def newgeneric_hotpath(name, signature, hot_path):
    from lalan.types.dispatch.generic import generic_with_hotpath
    assert issymbol(name)
    assert islist(signature)
    assert hot_path is not None

    obj = generic_with_hotpath(name, signature, hot_path)
    return obj


def isgeneric(w):
    from lalan.types.dispatch.generic import W_Generic
    return isinstance(w, W_Generic)


########################################################

def newtrait(name, constraints, signature, methods):
    from lalan.types.trait import trait
    from lalan.runtime import error
    error.affirm_type(name, issymbol)
    error.affirm_type(constraints, islist)
    error.affirm_type(signature, islist)
    error.affirm_type(methods, islist)
    error.affirm_iterable(signature, issymbol)
    error.affirm_iterable(constraints, isinterface)
    error.affirm_iterable(methods, istuple)

    return trait(name, constraints, signature, methods)


def istrait(w):
    from lalan.types.trait import W_Trait
    return isinstance(w, W_Trait)


########################################################

def newinterface(name, generics):
    from lalan.types.interface import interface
    from lalan.runtime import error
    error.affirm_type(name, issymbol)
    error.affirm_type(generics, islist)
    error.affirm_iterable(generics, isgeneric)

    return interface(name, generics)


def isinterface(w):
    from lalan.types.interface import W_Interface
    return isinstance(w, W_Interface)


########################################################

def newdatatype(process, name, fields):
    from lalan.types.datatype import newtype
    assert issymbol(name)
    return newtype(process, name, fields)


def newnativedatatype(name):
    from lalan.types.datatype import W_DataType
    assert issymbol(name)
    datatype = W_DataType(name, newlist([]))
    return datatype


def isdatatype(w):
    from lalan.types.datatype import W_DataType
    return isinstance(w, W_DataType)


def isextendable(w):
    from lalan.types.datatype import W_Extendable
    return isinstance(w, W_Extendable)


def isrecord(w):
    from lalan.types.datatype import W_Instance
    return isinstance(w, W_Instance)


def isdispatchable(w):
    from lalan.types.datatype import W_Instance, W_DataType
    return isinstance(w, W_Instance) or isinstance(w, W_DataType)


########################################################

def isoperator(w):
    from lalan.compile.parse.basic import W_Operator
    return isinstance(w, W_Operator)


############################################################

def newcoroutine(process, fn):
    from lalan.types.coroutine import newcoroutine
    assert isfunction(fn)
    return newcoroutine(process, fn)


def iscoroutine(co):
    from lalan.types.coroutine import W_Coroutine
    return isinstance(co, W_Coroutine)


############################################################


def safe_w(obj):
    if not isany(obj):
        s = "<PyObj type:%s, repr:%s>" % (type(obj), repr(obj))
        return newstring_s(s)
    return obj
