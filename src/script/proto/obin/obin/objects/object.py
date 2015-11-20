# encoding: utf-8
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rfloat import isnan, isinf, NAN, formatd, INFINITY
from rpython.rlib.objectmodel import enforceargs
from rpython.rlib import jit, debug

from obin.objects.object_map import new_map
from obin.runtime.exception import *
from obin.utils import tb
import api


class W_Root(object):
    _settled_ = True
    _immutable_fields_ = ['_type_']
    _type_ = ''

    def __str__(self):
        return self._tostring_()

    def __repr__(self):
        return self.__str__()

    def id(self):
        return str(hex(id(self)))

    def type(self):
        return self._type_

    # BEHAVIOR
    def _at_(self, b):
        raise NotImplementedError()

    def _lookup_(self, b):
        raise NotImplementedError()

    def _length_(self):
        raise NotImplementedError()

    def _put_(self, k, v):
        raise NotImplementedError()

    def _tostring_(self):
        raise NotImplementedError()

    def _tobool_(self):
        raise NotImplementedError()

    def _equal_(self, other):
        raise NotImplementedError()

    def _call_(self, ctx, args):
        raise NotImplementedError()

    def _compare_(self, other):
        raise NotImplementedError()


class W_Constant(W_Root):
    pass


class W_ValueType(W_Root):
    def value(self):
        raise NotImplementedError()


class W_Undefined(W_Constant):
    _type_ = 'Undefined'

    def _tostring_(self):
        return "undefined"


class W_Nil(W_Constant):
    _type_ = 'Nil'

    def _tostring_(self):
        return u'nil'

    def _tobool_(self):
        return False

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Nil, k)


class W_True(W_Constant):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def value(self):
        return True

    def _tostring_(self):
        return u'true'

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.True, k)

    def __str__(self):
        return '_True_'


class W_False(W_Constant):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def _tostring_(self):
        return u'false'

    def _tobool_(self):
        return False

    def value(self):
        return False

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.False, k)

    def __str__(self):
        return '_False_'


class W_Char(W_ValueType):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Char, self).__init__()
        self.__value = value

    def __str__(self):
        return '(%s)' % (unichr(self.__value),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return unichr(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Char, k)


class W_Integer(W_ValueType):
    _immutable_fields_ = ['__value']

    def __init__(self, value):
        super(W_Integer, self).__init__()
        self.__value = value

    # def __str__(self):
        # return 'W_Integer(%d)' % (self.value(),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Integer, k)


class W_Float(W_ValueType):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Float, self).__init__()
        self.__value = value

    # def __str__(self):
    #     return 'W_Float(%s)' % (str(self.__value),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Float, k)


class W_Cell(W_Root):
    def __init__(self):
        self.__frozen = False

    def freeze(self):
        self.__frozen = True

    def unfreeze(self):
        self.__frozen = False

    def isfrozen(self):
        return self.__frozen


class NativeListIterator(W_ValueType):
    def __init__(self, source, length):
        self.index = 0
        self.source = source
        self.length = length

    def _next_(self):
        from obin.objects.object_space import newundefined
        if self.index >= self.length:
            return newundefined()

        el = self.source[self.index]
        self.index += 1
        return el

    def _tostring_(self):
        return "<Iterator %d:%d>" % (self.index, self.length)

    def _tobool_(self):
        if self.index >= self.length:
            return False
        return True

class W_String(W_ValueType):
    _type_ = 'String'
    _immutable_fields_ = ['value']

    def __init__(self, value):
        assert value is not None and isinstance(value, unicode)
        super(W_String, self).__init__()
        self.__items = value
        self.__length = len(self.__items)

    # def __str__(self):
    #     return u'W_String("%s")' % (self.__items)

    def __eq__(self, other):
        if isinstance(other, unicode):
            raise RuntimeError("It is not unicode")
        if isinstance(other, str):
            raise RuntimeError("It is not  str")
        if not isinstance(other, W_String):
            return False
        return self.value() == other.value()

    def __hash__(self):
        return self.value().__hash__()

    def isempty(self):
        return not bool(len(self.__items))

    def value(self):
        return self.__items

    def _tostring_(self):
        return str(self.__items)

    def _iterator_(self):
        return NativeListIterator(self.__items, self.__length)

    def _tobool_(self):
        return bool(self.__items)

    def _length_(self):
        return self.__length

    def _at_(self, index):
        from object_space import newundefined, newchar, isint
        assert isint(index)
        try:
            ch = self.__items[index.value()]
        except ObinKeyError:
            return newundefined()

        return newchar(ch)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.String, k)


class W_Vector(W_Cell):
    _type_ = 'Vector'

    def __init__(self, items=None):
        super(W_Vector, self).__init__()
        if not items:
            items = []
        assert isinstance(items, list)
        self._items = items

    # def __str__(self):
    #     return u'W_Vector("%s")' % str(self._items)

    def _put_(self, k, v):
        if self.isfrozen():
            raise ObinRuntimeError("Vector is frozen")
        from object_space import isint
        if not isint(k):
            raise ObinKeyError(k)
        i = k.value()
        try:
            self._items[i] = v
        except:
            raise ObinKeyError(k)

    def _lookup_(self, k):
        from object_space import object_space, isint
        return api.at(object_space.traits.Vector, k)

    def _at_(self, index):
        from object_space import newundefined, isint
        assert isint(index)
        try:
            el = self._items[index.value()]
        except ObinKeyError:
            return newundefined()

        return el

    def _iterator_(self):
        return NativeListIterator(self._items, self.length())

    def _tobool_(self):
        return bool(self._items)

    def _length_(self):
        return self.length()

    def _delete_(self, key):
        del self._items[key]

    def _tostring_(self):
        return str(self._items)

    def at(self, i):
        return self._items[i]

    def has_index(self, i):
        return i > 0 and i < self.length()

    def get_index(self, obj):
        try:
            return self._items.index(obj)
        except KeyError:
            return -1

    def has(self, obj):
        return obj in self._items

    def length(self):
        return len(self._items)

    def append(self, v):
        self._items.append(v)

    def prepend(self, v):
        self._items.insert(0, v)

    def insert(self, index, v):
        self._items.insert(index, v)

    def remove(self, v):
        self._items.remove(v)

    def values(self):
        return self._items

    def pop(self):
        return self._items.pop()

class W_Object(W_Cell):
    _type_ = 'Object'
    _immutable_fields_ = ['_type_']

    def __init__(self, slots):
        super(W_Object, self).__init__()
        from obin.objects.datastructs import Slots
        if not slots:
            slots = Slots()
        self.__slots = slots
        self.__traits = None

    def has_traits(self):
        return self.__traits is not None

    def create_traits(self, traits):
        assert self.traits() is None
        if not traits:
            traits = W_Vector()

        self.__traits = traits

    # def __str__(self):
    #     return "W_Object(%s)" % (self._tostring_())

    def put_by_index(self, idx, value):
        self.__slots.set_by_index(idx, value)

    def get_by_index(self, idx):
        return self.__slots.get_by_index(idx)

    def traits(self):
        return self.__traits

    def isa(self, obj):
        assert isinstance(obj, W_Object)
        if self is obj:
            return

        if not self.traits().has(obj):
            self.traits().prepend(obj)

        for trait in obj.traits().values():
            index = self.traits().get_index(trait)
            if index == -1:
                self.traits().prepend(trait)
            else:
                self.traits().insert(index, trait)

    def nota(self, obj):
        assert isinstance(obj, W_Object)
        if self is obj:
            return

        try:
            self.traits().remove(obj)
        except KeyError:
            pass

        for trait in obj.traits().values():
            try:
                self.traits().remove(trait)
            except KeyError:
                pass

    def kindof(self, obj):
        if obj is self:
            return True

        assert isinstance(obj, W_Object)
        if not self.traits().has(obj):
            return False

        for t in obj.traits().values():
            if not self.traits().has(t):
                return False

        return True

    def has(self, k):
        from object_space import isundefined
        v = self._at_(k)
        return not isundefined(v)

    def _lookup_(self, k):
        from object_space import isundefined, newundefined
        v = self._at_(k)
        if not isundefined(v):
            return v

        for t in self.traits().values():
            v = t._at_(k)
            if not isundefined(v):
                return v

        return newundefined()

    def _at_(self, k):
        from object_space import newundefined
        v = self.__slots.get(k)
        if v is None:
            return newundefined()

        return v

    def _call_(self, ctx, args):
        from object_space import newstring, isundefined
        cb = self._at_(newstring("__call__"))
        if isundefined(cb):
            raise ObinRuntimeError("Object is not callable")

        args.insert(0, self)
        return api.call(cb, ctx, args)

    def _put_(self, k, v):
        if self.isfrozen():
            raise ObinRuntimeError("Object is frozen")
        self.__slots.add(k, v)

    def _iterator_(self):
        keys = self.__slots.keys()
        return NativeListIterator(keys, len(keys))

    def _tobool_(self):
        return True

    def _length_(self):
        return self.__slots.length()

    def _tostring_(self):
        from object_space import newstring, isundefined

        _name_ = self._at_(newstring("__name__"))
        if isundefined(_name_):
            return str(self.__slots)
        else:
            return "<object %s %s>" % (_name_._tostring_(), self.id())

    def _clone_(self):
        import copy
        slots = copy.copy(self.__slots)
        clone = W_Object(slots)

        traits = copy.copy(self.__traits)
        clone.create_traits(traits)
        return clone


class W_Module(W_Root):
    def __init__(self, name, bytecode):
        self._name = name
        self._bytecode_ = bytecode
        self._object_ = None
        self._result_ = None
        self._is_compiled_ = False
        self.init_scope()

    def init_scope(self):
        self._object_ = self._bytecode_.scope.create_object()

    def result(self):
        return self._result_

    def set_result(self, r):
        self._result_ = r

    def code(self):
        return self._bytecode_

    def scope(self):
        return self._object_

    def compile(self):
        assert not self._is_compiled_
        from obin.runtime.routine import create_bytecode_routine
        from obin.runtime.context import create_object_context

        routine = create_bytecode_routine(self._bytecode_)

        print "*********"
        for i, c in enumerate([str(c) for c in self._bytecode_.compiled_opcodes]): print i,c
        print "*********"

        create_object_context(routine, self._object_)
        self._is_compiled_ = True
        return routine


class W_Function(W_Root):
    _type_ = 'function'
    _immutable_fields_ = ['_type_',  '_scope_',  '_variadic_', '_arity_', '_name_']

    def __init__(self, name, bytecode, scope):
        super(W_Function, self).__init__()
        self._name_ = name
        self._bytecode_ = bytecode
        self._arity_ = len(bytecode.params())
        if bytecode.params_rest() is not None:
            self._variadic_ = True
        else:
            self._variadic_ = False

        self._scope_ = scope

    def arity(self):
        return self._arity_

    def is_variadic(self):
        return self._variadic_

    def _tostring_(self):
        params = ",".join([str(p.value()) for p in self._bytecode_.params()])

        return "fn %s(%s){ %s }" % (self._name_.value(), params, self._bytecode_.tostring())

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Function, k)

    # def __str__(self):
    #     return 'Function %s' % self._tostring_()

    def create_routine(self, ctx, args):
        from obin.runtime.context import create_function_context
        from obin.runtime.routine import create_function_routine

        routine = create_function_routine(self._bytecode_, self._name_)

        jit.promote(routine)
        scope = self.scope()

        create_function_context(routine,
                                args,
                                scope)
        return routine

    def _call_(self, ctx, args):
        assert ctx
        # if ctx is None:
        #     from object_space import object_space
        #     ctx = object_space.interpreter.machine.current_context()

        ctx.process().call_object(self, ctx, args)

    def scope(self):
        return self._scope_

class W_Primitive(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ['_type_', '_extensible_', '_scope_', '_params_[*]', '_function_']

    def __init__(self, name, function):
        super(W_Primitive, self).__init__()
        self._name_ = name
        self._function_ = function

    def _tostring_(self):
        return "function %s {[native code]}" % self._name_.value()

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Function, k)

    def create_routine(self, ctx, args):
        from obin.runtime.context import create_primitive_context
        from obin.runtime.routine import NativeRoutine

        routine = NativeRoutine(self._name_, self._function_)

        jit.promote(routine)

        create_primitive_context(routine,
                                 args)
        return routine

    def _call_(self, ctx, args):
        assert ctx
        # if ctx is None:
        #     from object_space import object_space
        #     ctx = object_space.interpreter.machine.current_context()

        ctx.process().call_object(self, ctx, args)

class W_CoroutineIterator(W_Root):
    def __init__(self, coroutine):
        self._coroutine_ = coroutine

    def _tobool_(self):
        return self._coroutine_.is_accessible()

    def _next_(self):
        from object_space import object_space, newundefined, newinterrupt
        process = object_space.interpreter.process
        routine = process.routine()
        self._coroutine_._call_(routine.ctx, None)
        return newinterrupt()

    def _tostring_(self):
        return "CoroutineIterator"


class W_CoroutineYield(W_Root):
    def __init__(self, coroutine):
        self._coroutine_ = coroutine
        self._receiver_ = None

    def coroutine(self):
        return self._coroutine_

    def set_receiver(self, continuation):
        self._receiver_ = continuation

    def _tostring_(self):
        return "fn coroutine.yield {[native code]}"

    def _tobool_(self):
        return True

    def _call_(self, ctx, args):
        if not self._coroutine_.is_accessible():
            raise ObinRuntimeError(u"Can not yield from coroutine")

        assert ctx
        routine = ctx.routine()
        self._coroutine_.set_receiver(routine)

        ctx.process().yield_to_routine(self._receiver_, routine, args[0])



class W_Coroutine(W_Root):
    _type_ = 'native'
    _immutable_fields_ = ['_function_']

    def __init__(self, function):
        super(W_Coroutine, self).__init__()
        self._function_ = function
        self._routine_ = None
        self._receiver_ = None
        self._yield_ = None

    def is_accessible(self):
        return self._routine_ is None or not self._routine_.is_closed()

    def function(self):
        return self._function_

    def set_receiver(self, co):
        # from obin.runtime.process import check_continuation_consistency
        # if self._receiver_:
        #     check_continuation_consistency(self._receiver_, co)
        self._receiver_ = co

    def _tostring_(self):
        return "fn coroutine {[native code]}"

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Coroutine, k)

    def _first_call_(self, ctx, args):
        self._receiver_ = ctx.routine()

        self._yield_ = W_CoroutineYield(self)
        self._yield_.set_receiver(self._receiver_)

        if args is not None:
            args.insert(0, self._yield_)
        else:
            args = [self._yield_]

        self._routine_ = self.function().create_routine(ctx, args)
        ctx.process().call_routine(self._routine_, self._receiver_, self._receiver_)

    def _iterator_(self):
        return W_CoroutineIterator(self)

    def _call_(self, ctx, args):
        from object_space import newundefined
        assert ctx

        if not self._routine_:
            return self._first_call_(ctx, args)

        if not self._routine_.is_suspended():
            raise ObinRuntimeError(u"Invalid coroutine state")

        if args is not None:
            value = args[0]
        else:
            value = newundefined()

        receiver = ctx.routine()
        self._yield_.set_receiver(receiver)
        ctx.process().yield_to_routine(self._receiver_, receiver, value)


















# class TRYCATCHBLOCK(Opcode):
#     _immutable_fields_ = ['tryexec', 'catchexec', 'catchparam', 'finallyexec']
#
#     def __init__(self, tryfunc, catchparam, catchfunc, finallyfunc):
#         self.tryroutine = tryfunc
#         self.catchroutine = catchfunc
#         self.catchparam = catchparam
#         self.finallyroutine = finallyfunc
#
#     def stack_change(self):
#         trystack = 0
#         catchstack = 0
#         finallystack = 0
#
#         if self.tryroutine is not None:
#             trystack = self.tryroutine.estimated_stack_size()
#             #if self.catchexec is not None:
#             #catchstack = self.catchexec.estimated_stack_size()
#         if self.finallyroutine is not None:
#             finallystack = self.finallyroutine.estimated_stack_size()
#
#         return trystack + catchstack + finallystack
#
#     def eval(self, ctx):
#         from obin.runtime.context import BlockExecutionContext
#         tryroutine = self.tryroutine.clone()
#         catchroutine = self.catchroutine.clone()
#
#         finallroutine = self.finallyroutine.clone() if self.finallyroutine else None
#         parentroutine = ctx.routine()
#
#         stack_p = ctx.stack_pointer()
#
#         trycontext = BlockExecutionContext(tryroutine, ctx)
#         tryroutine.add_signal_handler(None, catchroutine)
#         catchcontext = BlockExecutionContext(catchroutine, ctx)
#         continuation = None
#         if finallroutine:
#             finallycontext = BlockExecutionContext(finallroutine, ctx)
#             # print "finallroutine.estimated_stack_size()", finallroutine.estimated_stack_size()
#             # print finallroutine.code()
#
#             continuation = finallroutine
#             catchroutine.set_continuation(finallroutine)
#             finallroutine.set_continuation(parentroutine)
#         else:
#             catchroutine.set_continuation(parentroutine)
#             continuation = parentroutine
#
#         catchroutine.set_start_stack_index(stack_p)
#         ctx.routine().fiber.call_routine(tryroutine, continuation, parentroutine)

