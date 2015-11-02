# encoding: utf-8
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rfloat import isnan, isinf, NAN, formatd, INFINITY
from rpython.rlib.objectmodel import enforceargs
from rpython.rlib import jit, debug

from obin.objects.object_map import new_map
from obin.runtime.exception import *
from obin.utils import tb
import api

@jit.elidable
def is_array_index(p):
    return make_array_index(p) != NOT_ARRAY_INDEX

NOT_ARRAY_INDEX = -1

class Descr(object):
    def __init__(self, can_put, own, inherited, prop):
        self.can_put = can_put
        self.own = own
        self.inherited = inherited
        self.prop = prop

@jit.unroll_safe
def make_array_index(idx):
    if len(idx) == 0:
        return -1

    IDX_LIT = '0123456789'

    for c in idx:
        if c not in IDX_LIT:
            return NOT_ARRAY_INDEX
    return int(idx)


@jit.elidable
def sign(i):
    if i > 0:
        return 1
    if i < 0:
        return -1
    return 0

class W_Root(object):
    _settled_ = True
    _immutable_fields_ = ['_type_']
    _type_ = ''

    def __str__(self):
        return api.tostring(self)

    def type(self):
        return self._type_

    # BEHAVIOR
    def _at_(self, b):
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

class W_Primitive(W_Root):
    pass

class W_Undefined(W_Primitive):
    _type_ = 'Undefined'

class W_Nil(W_Primitive):
    _type_ = 'Nil'

    def _tostring_(self):
        return u'nil'

    def _tobool_(self):
        return False

    def _at_(self, k):
        from object_space import object_space

        return api.at(object_space.traits.Nil, k)

class W_True(W_Primitive):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def _tostring_(self):
        return u'true'

    def _tobool_(self):
        return True

    def _at_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.True, k)

    def __str__(self):
        return '_True_'

class W_False(W_Primitive):
    _type_ = 'True'
    _immutable_fields_ = ['value']

    def _tostring_(self):
        return u'false'

    def _tobool_(self):
        return False

    def _at_(self, k):
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

    def _at_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Char, k)

class W_Integer(W_Primitive):
    _immutable_fields_ = ['__value']

    def __init__(self, value):
        super(W_Integer, self).__init__()
        self.__value = value

    def __str__(self):
        return 'W_Integer(%d)' % (self.value,)

    def value(self):
        return self.__value

    def _tostring_(self):
        return str(self.__value)

    def _tobool_(self):
        return bool(self.__value)

    def _at_(self, k):
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

    def _at_(self, k):
        from object_space import object_space
        return api.at(object_space.traits.Float, k)

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

    def _tostring_(self):
        return str(self.__items)

    def _iterator_(self):
        return LinearSequenceIterator(self, self.__length)

    def _tobool_(self):
        return bool(self.__items)

    def _length_(self):
        return self.__length

    def _at_(self, k):
        from object_space import object_space, isint
        if isint(k):
            return self._char_at(k.value())
        else:
            return api.at(object_space.traits.String, k)

    def _char_at(self, index):
        from object_space import newundefined, newchar
        try:
            ch = self.__items[index]
        except KeyError:
            return newundefined()

        return newchar(ch)

class W_Array(W_Primitive):
    _type_ = 'Array'
    _immutable_fields_ = ['__length']

    def __init__(self, items=None):
        super(W_Array, self).__init__()

        if not items:
            items = []
        assert isinstance(items, list)
        self._items = items
        self._length = len(self._items)

    def __str__(self):
        return u'W_Array("%s")' % (self._items)

    def _put_(self, k, v):
        from object_space import object_space, isint
        if not isint(k):
            raise JsKeyError("Integer key expected", k)
        i = k.value()
        try:
            self._items[i] = v
        except:
            raise JsKeyError("Invalid index ", k)

    def _at_(self, k):
        from object_space import object_space, isint
        if isint(k):
            return self._at_index_(k.value())
        else:
            return api.at(object_space.traits.Array, k)

    def __str__(self):
        return u'W_Array("%s")' % (self._items)

    def _tostring_(self):
        return str(self._items)

    def _iterator_(self):
        return LinearSequenceIterator(self, self._length)

    def _tobool_(self):
        return bool(self._items)

    def _length_(self):
        return self._length

    def at(self, i):
        return self._items[i]

    def _at_index_(self, index):
        from object_space import newundefined
        try:
            el = self._items[index]
        except KeyError:
            return newundefined()

        return el

class W_Tuple(W_Array):
    _type_ = 'Tuple'
    _immutable_fields_ = ['__length']

    def __init__(self, items):
        super(W_Tuple, self).__init__()
        assert isinstance(items, list)
        self._items = tuple(items)
        self._length = len(self._items)

    def __str__(self):
        return u'W_Tuple("%s")' % str(self._items)

    def _put(self, k, v):
        raise NotImplementedError()

    def _at_(self, k):
        from object_space import object_space, isint
        if isint(k):
            return self._at_index_(k.value())
        else:
            return api.at(object_space.traits.Tuple, k)

class W_Vector(W_Array):
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
        from object_space import object_space, isint
        if not isint(k):
            raise JsKeyError(k)
        i = k.value()
        try:
            self._items[i] = v
        except:
            raise JsKeyError(k)

    def _at_(self, k):
        from object_space import object_space, isint
        if isint(k):
            return self._at_index_(k.value())
        else:
            return api.at(object_space.traitsVector, k)

    def _iterator_(self):
        return LinearSequenceIterator(self, self._length)

    def _tobool_(self):
        return bool(self._items)

    def _length_(self):
        return self.length()

    def at(self, i):
        return self._items[i]

    def length(self):
        return len(self._items)

    def _at_index_(self, index):
        from object_space import newundefined
        try:
            el = self._items[index]
        except KeyError:
            return newundefined()

        return el

    def append(self, v):
        self._items.append(v)

    def pop(self, v):
        self._items.append(v)

    def _delete_(self, key):
        del self._items[key]


class W_Object(W_Root):
    _type_ = 'object'
    _extensible_ = True
    _immutable_fields_ = ['_type_']

    def __init__(self):
        from obin.objects.datastructs import Slots
        self._slots = Slots()

    def __str__(self):
        return "%s: %s" % (object.__repr__(self), self._type_)

    #TODO rename to freeze
    def extensible(self):
        return self._extensible_

    # 8.12.3
    def get(self, p):
        assert p is not None
        if not isinstance(p, unicode):
            p = p.to_string()

        obj = self.get_property(p)
        if obj is None:
            raise JsTypeError(p)
        return obj

    # 8.12.2
    def get_property(self, p):
        assert p is not None and isinstance(p, unicode)

        prop = self.get_own_property(p)
        if prop is not None:
            return prop

        return self.get_outer_property(p)

    def get_outer_property(self, p):
        return None

    # 8.12.1
    def get_own_property(self, p):
        assert p is not None and isinstance(p, unicode)
        return self._get_prop(p)

    def _get_prop(self, name):
        prop = self._slots.get(name)
        return prop

    def _del_prop(self, name):
        self._slots.delete(name)

    def _add_prop(self, name, value):
        self._slots.add(name, value)

    # 8.12.5
    def put(self, p, v):
        assert p is not None
        if not isinstance(p, unicode):
            p = p.to_string()

        #it works like freeze now but you can determine outer set and inner later
        if not self.extensible():
            raise JsTypeError(u"can't put %s" % (p, ))

        self._add_prop(p, v)

    # 8.12.6
    def has_property(self, p):
        assert p is not None and isinstance(p, unicode)
        return self._slots.contains(p)

    # 8.12.7
    def delete(self, p):
        self._del_prop(p)

    # 8.12.8
    def default_value(self, hint='Number'):
        from obin.objects.object_space import newstring
        if hint == 'String':
            res = self._default_value_string_()
            if res is None:
                res = self._default_value_number_()
        else:
            res = self._default_value_number_()
            if res is None:
                res = self._default_value_string_()

        if res is not None:
            return res

        return newstring(u"Object")

    def _default_value_string_(self):
        to_string = self.get(u'toString')
        from obin.runtime.machine import run_function_for_result
        if to_string.is_callable():
            assert isinstance(to_string, W_BasicFunction)

            _str = run_function_for_result(to_string, this=self)
            return _str

    def _default_value_number_(self):
        from obin.runtime.machine import run_function_for_result
        value_of = self.get(u'valueOf')
        if value_of.is_callable():
            assert isinstance(value_of, W_BasicFunction)
            val = run_function_for_result(value_of, this=self)
            return val

    def ToNumber(self):
        return 0

    ##########
    def to_boolean(self):
        return True

    def to_string(self):
        if self._default_value_string_() is None:
            print self._default_value_string_()
            return u""

        return self._default_value_string_().to_string()

    def ToObject(self):
        return self

    def has_instance(self, other):
        raise JsTypeError(u'has_instance')

    def named_properties(self):
        return self._slots.keys()


class W_BasicObject(W_Object):
    def __init__(self):
        W_Object.__init__(self)
        from obin.objects.object_space import newnull
        W_BasicObject.put(self, u'__proto__', newnull())
        self._prototype_ = newnull()

    def prototype(self):
        return self._prototype_

    def get_outer_property(self, p):
        from obin.objects.object_space import isnull
        proto = self.prototype()
        if isnull(proto):
            return None
        if not isinstance(proto, W_BasicObject):
            raise JsRangeError()
        return proto.get_property(p)

class W__Object(W_BasicObject):
    pass


class W_ModuleObject(W__Object):
    pass


class W_BasicFunction(W_BasicObject):

    def Call(self, args=[], this=None, calling_context=None):
        raise NotImplementedError("abstract")

    def is_callable(self):
        return True

    def _to_string_(self):
        return u'function() {}'

    # 15.3.5.3
    def has_instance(self, v):
        from obin.objects.object_space import isnull_or_undefined
        if not isinstance(v, W_BasicObject):
            return False

        o = self.get(u'prototype')

        if not isinstance(o, W_BasicObject):
            raise JsTypeError(u'has_instance')

        while True:
            assert isinstance(v, W_BasicObject)
            v = v.prototype()
            if isnull_or_undefined(v):
                return False
            if v == o:
                return True

class W__Function(W_BasicFunction):
    _type_ = 'function'
    _immutable_fields_ = ['_type_', '_extensible_', '_scope_', '_params_[*]', '_function_']

    def __init__(self, function_body, formal_parameter_list=[], scope=None):
        W_BasicFunction.__init__(self)
        from obin.objects.object_space import _w, newnull, object_space
        # print "W__Function", function_body.__class__, scope, formal_parameter_list
        self._function_ = function_body
        self._scope_ = scope
        self._params_ = formal_parameter_list
        # 13.2 Creating Function Objects
        # 14.
        _len = len(formal_parameter_list)
        # 15.
        put_property(self, u'length', _w(_len),)
        # 16.
        proto_obj = object_space.new_obj()
        # 18.
        put_property(self, u'prototype', proto_obj)

        put_property(self, u'caller', newnull())

    def _to_string_(self):
        return self._function_.to_string()

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

class W_List(W_Root):
    def __init__(self, values):
        assert isinstance(values, list)
        self.values = values

    def to_list(self):
        return self.values

    def __str__(self):
        return 'W_List(%s)' % (unicode([unicode(v) for v in self.values]))


class W_Iterator(W_Root):
    def __init__(self, elements_w):
        self.elements_w = elements_w

    def next(self):
        if self.elements_w:
            return self.elements_w.pop()

    def empty(self):
        return len(self.elements_w) == 0

    def to_string(self):
        return u'<Iterator>'



def put_property(obj, name, value):
    obj.put(name, value)
