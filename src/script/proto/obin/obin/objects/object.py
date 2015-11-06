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

    def _compare_(self, other):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

class W_Constant(W_Root):
    pass

class W_Primitive(W_Root):
    pass

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

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.False, k)

    def __str__(self):
        return '_False_'

class W_Char(W_Primitive):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Char, self).__init__()
        self.__value = value

    def __str__(self):
        return 'W_Char(%s)' % (unichr(self.__value),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return unichr(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Char, k)

class W_Integer(W_Primitive):
    _immutable_fields_ = ['__value']

    def __init__(self, value):
        super(W_Integer, self).__init__()
        self.__value = value

    def __str__(self):
        return 'W_Integer(%d)' % (self.value(),)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Integer, k)

class W_Float(W_Primitive):
    _immutable_fields_ = ['value']

    def __init__(self, value):
        super(W_Float, self).__init__()
        self.__value = value

    def __str__(self):
        return 'W_Float(%d)' % (self.__value,)

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

class LinearSequenceIterator(W_Primitive):
    def __init__(self, source, length):
        self.index = 0
        self.source = source
        self.length = length

    def _next_(self):
        from obin.objects.object_space import newundefined
        if self.index >= self.length:
            return newundefined()

        return api.at(self.source, self.index)


class W_String(W_Primitive):
    _type_ = 'String'
    _immutable_fields_ = ['value']

    def __init__(self, value):
        assert value is not None and isinstance(value, unicode)
        super(W_String, self).__init__()
        self.__items = value
        self.__length = len(self.__items)

    def __str__(self):
        return u'W_String("%s")' % (self.__items)

    def __eq__(self, other):
        if not isinstance(other, W_String):
            return False
        return self.value() == other.value()

    def __hash__(self):
        return self.value().__hash__()

    def value(self):
        return self.__items

    def _tostring_(self):
        return str(self.__items)

    def _iterator_(self):
        return LinearSequenceIterator(self, self.__length)

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

    def __str__(self):
        return u'W_Vector("%s")' % str(self._items)

    def _put_(self, k, v):
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
        return api.at(object_space.traitsVector, k)

    def _at_(self, index):
        from object_space import newundefined, isint
        assert isint(index)
        try:
            el = self._items[index.value()]
        except ObinKeyError:
            return newundefined()

        return el

    def _iterator_(self):
        return LinearSequenceIterator(self, self.length())

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

class W_ObjectIterator(W_Primitive):
    def __init__(self, keys):
        self.index = 0
        self.keys = keys
        self.length = len(self.keys)

    def _next_(self):
        from obin.objects.object_space import newundefined
        if self.index >= self.length:
            return newundefined()

        return self.keys[self.index]

class W_Object(W_Cell):
    _type_ = 'Object'
    _immutable_fields_ = ['_type_']

    def __init__(self, slots, traits):
        super(W_Object, self).__init__()
        from obin.objects.datastructs import Slots
        if not slots:
            slots = Slots()
        if not traits:
            traits = W_Vector()

        self.__slots = slots
        self.__traits = traits

    def __str__(self):
        return "%s: %s" % (object.__repr__(self), self._type_)

    def traits(self):
        return self.__traits

    def isa(self, obj):
        assert isinstance(obj, W_Object)
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

    def _put_(self, k, v):
        self.__slots.add(k, v)

    def _iterator_(self):
        return W_ObjectIterator(self.__slots.keys())

    def _tobool_(self):
        return True

    def _length_(self):
        return self.__slots.length()

    def _tostring_(self):
        return str(self.__slots)

    def _clone_(self):
        import copy
        slots = copy.copy(self.__slots)
        traits = copy.copy(self.__traits)
        clone = W_Object(slots, traits)
        return clone

class W_ModuleObject(W_Object):
    pass

class W_Function(W_Primitive):
    _type_ = 'function'
    _immutable_fields_ = ['_type_', '_extensible_', '_scope_', '_params_[*]', '_function_']

    def __init__(self, function_body, formal_parameter_list=[], scope=None):
        from obin.objects.object_space import newint

        super(W_Function, self).__init__()
        # print "W__Function", function_body.__class__, scope, formal_parameter_list
        self._function_ = function_body
        self._scope_ = scope
        self._params_ = formal_parameter_list

    def _tostring_(self):
        return self._function_.to_string()

    def _tobool_(self):
        return True

    def _lookup_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Function, k)

    def __str__(self):
        return 'Function %s' % self._tostring_()

    def code(self):
        return self._function_

    def formal_parameters(self):
        return self._params_

    def create_routine(self, args=[], this=None, calling_context=None):
        from obin.runtime.execution_context import FunctionExecutionContext
        code = self.code().clone()
        jit.promote(code)
        scope = self.scope()

        ctx = FunctionExecutionContext(code,
                                       argv=args,
                                       this=this,
                                       scope=scope,
                                       w_func=self)
        ctx._calling_context_ = calling_context
        code.set_context(ctx)
        return code

    def Call(self, args=[], this=None, calling_context=None):
        if calling_context is None:
            from object_space import object_space
            calling_context = object_space.interpreter.machine.current_context()

        calling_context.fiber().call_object(self, args, this, calling_context)

    def scope(self):
        return self._scope_

