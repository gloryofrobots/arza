# encoding: utf-8
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rfloat import isnan, isinf, NAN, formatd, INFINITY
from rpython.rlib.objectmodel import enforceargs
from rpython.rlib import jit, debug

from obin.object.property_descriptor import PropertyDescriptor, DataPropertyDescriptor, AccessorPropertyDescriptor, is_data_descriptor, is_generic_descriptor, is_accessor_descriptor
from obin.object.property import DataProperty, AccessorProperty
from obin.object.datastructs import *
from obin.exception import JsTypeError, JsRangeError


class W_Root(object):
    _settled_ = True
    _immutable_fields_ = ['_type_']
    _type_ = ''

    def __str__(self):
        return self.to_string()

    def to_string(self):
        raise NotImplementedError()

    def type(self):
        return self._type_

class W_Primitive(W_Root):
    pass

class W_Undefined(W_Root):
    _type_ = 'Nothing'

    def to_string(self):
        return u'Nothing'

class W_Null(W_Primitive):
    _type_ = 'Nil'

    def to_boolean(self):
        return False

    def to_string(self):
        return u'Nil'

    def to_object(self):
        raise JsTypeError(u'W_Null.ToObject')


class PropertyIdenfidier(object):
    def __init__(self, name, descriptor):
        self.name = name
        self.descriptor = descriptor

def reject(throw, msg=u''):
    if throw:
        raise JsTypeError(msg)
    return False

def _ireject(throw, idx):
    if throw:
        raise JsTypeError(unicode(str(idx)))
    return False

def newgetter(name):
    class __Getter(W_Root):
        def __init__(self, name, attrname):
            self.name = name
            self.attrname = attrname

        def is_callable(self):
            return True

        def Call(self, args=[], this=None, calling_context=None):
            if not isinstance(this, W_Object):
                raise JsTypeError(u'')

            return getattr(this, self.name)
    return __Getter(name)

def newsetter(name):
    class __Setter(W_Root):
        def __init__(self, name):
            self.name = name

        def is_callable(self):
            return True

        def Call(self, args=[], this=None, calling_context=None):
            if not isinstance(this, W_Object):
                raise JsTypeError(u'')

            value = args[0]
            setattr(this, self.name, value)
    return __Setter(name)

delegates_desc = AccessorPropertyDescriptor(newgetter(u"__delegates__"),
                                            newsetter(u"__delegates__"), False, False)
jit.promote(delegates_desc)

frozen_desc = AccessorPropertyDescriptor(newgetter(u"__frozen__"),
                                            newsetter(u"__frozen__"), False, False)
jit.promote(frozen_desc)

name_desc = AccessorPropertyDescriptor(newgetter(u"__name__"),
                                            newsetter(u"_frozen__"), False, False)
jit.promote(name_desc)

class W_Object(W_Root):
    _type_ = 'object'
    _extensible_ = True
    _immutable_fields_ = ['_type_']  # TODO why need _primitive_value_ here???

    def __init__(self):
        from obin.object.space import newnull, newbool
        self.slots = newslots()
        self.__delegates__ = newnull()
        self.__frozen__ = newbool(False)
        self._name_ = newnull()
        W_Object.define_own_property(self, u'__delegates__', delegates_desc)
        W_Object.define_own_property(self, u'__frozen__', frozen_desc)

    def __str__(self):
        return "%s: %s" % (object.__repr__(self), self.type())

    def _init_delegates(self, delegates):
        from obin.object.space import isnull_or_undefined, _w
        assert isnull_or_undefined(self.__delegates__)
        assert isinstance(delegates, list)
        self.__delegates__ = _w(delegates)

    #TODO add delegate both as property and in list
    #add as property if delegate has a name
    def add_delegate(self, delegate):
        from obin.object.space import isnull_or_undefined, _w, newvector_with_elements
        if isnull_or_undefined(self.__delegates__):
            self._init_delegates([delegate])
        self.__delegates__.push(delegate)


    def isfrozen(self):
        return self.__frozen__.to_boolean()

    def delegates(self):
        return self.__delegates__

    ##########
    # 8.12.3
    def get(self, p):
        assert p is not None and isinstance(p, unicode)
        desc = self.get_property(p)
        return self._get_from_desc(desc)

    def _get_from_desc(self, desc):
        assert desc is not None

        if is_data_descriptor(desc):
            return desc.value

        if desc.has_set_getter() is False:
            raise JsTypeError("Property not exists")

        getter = desc.getter
        res = getter.Call(this=self)
        return res

    # 8.12.2
    def get_property(self, p):
        assert p is not None and isinstance(p, unicode)

        prop = self.get_own_property(p)
        if prop is not None:
            return prop

        return self._get_from_delegates(p)

    def _get_from_delegates(self, p):
        from obin.object.space import isundefined
        delegates = self.delegates()

        if not isinstance(delegates, list):
            return delegates.get_property(p)

        if isundefined(delegates):
            return None

        for delegate in delegates:
            result = delegate.get_property(p)
            if result:
                return result

        return None


    # 8.12.1
    def get_own_property(self, p):
        assert p is not None and isinstance(p, unicode)

        prop = self._get_prop(p)
        if prop is None:
            return

        return prop.to_property_descriptor()

    def _get_prop(self, name):
        return self.slots.get(name)

    def _del_prop(self, name):
        self.slots.delete(name)

    def _add_prop(self, name, value):
        self.slots.add(name, value)

    def _set_prop(self, name, value):
        self.slots.set(name, value)


    # 8.12.5
    def put(self, p, v):
        assert p is not None and isinstance(p, unicode)

        if not self.can_put(p):
            raise JsTypeError(u"can't put %s" % (p, ))

        own_desc = self.get_own_property(p)
        if own_desc is None:
            new_desc = DataPropertyDescriptor(v, True, True, True)
            self.define_own_property(p, new_desc)
        elif is_data_descriptor(own_desc) is True:
            value_desc = PropertyDescriptor(value=v)
            self.define_own_property(p, value_desc)
        elif is_accessor_descriptor(own_desc) is True:
            setter = own_desc.setter
            assert setter is not None
            setter.Call(this=self, args=[v])
        else:
            raise JsTypeError("Unknown description")

    def w_put(self, w_p, v):
        name = w_p.to_string()
        self.put(name, v)

    # 8.12.4
    def can_put(self, p):
        from obin.object.space import isundefined
        if self.isfrozen():
            return False

        desc = self.get_own_property(p)
        if desc is None:
            return False

        if is_accessor_descriptor(desc) is True:
            if isundefined(desc.setter):
                return False
            else:
                return True

        return desc.writable

    # 8.12.6
    def has_property(self, p):
        assert p is not None and isinstance(p, unicode)

        desc = self.get_property(p)
        if desc is None:
            return False
        return True

    # 8.12.7
    def delete(self, p):
        desc = self.get_own_property(p)
        if desc is None:
            raise JsTypeError(u"Property not exists")

        if desc.configurable:
            self._del_prop(p)
            return True

        raise JsTypeError(u"Property %s non deletable" % str(p))

    # 8.12.9
    def define_own_property(self, p, desc):
        assert desc is not None
        current = self.get_own_property(p)
        isfrozen = self.isfrozen()
        throw = True
        # 3.
        if current is None and isfrozen is True:
            return reject(throw, p)

        # 4.
        if current is None and isfrozen is False:
            # 4.a
            if is_generic_descriptor(desc) or is_data_descriptor(desc):
                new_prop = DataProperty(
                    desc.value,
                    desc.writable,
                    desc.enumerable,
                    desc.configurable
                )
                self._add_prop(p, new_prop)
            # 4.b
            else:
                assert is_accessor_descriptor(desc) is True
                new_prop = AccessorProperty(
                    desc.getter,
                    desc.setter,
                    desc.enumerable,
                    desc.configurable
                )
                self._add_prop(p, new_prop)
            # 4.c
            return True

        # 5.
        if desc.is_empty():
            return True

        # 6.
        if desc == current:
            return True

        # 7.
        if current.configurable is False:
            if desc.configurable is True:
                return reject(throw, p)
            if desc.has_set_enumerable() and current.enumerable != desc.enumerable:
                return reject(throw, p)

        # 8.
        if is_generic_descriptor(desc):
            pass
        # 9.
        elif is_data_descriptor(current) != is_data_descriptor(desc):
            # 9.a
            if current.configurable is False:
                return reject(throw, p)
            # 9.b
            if is_data_descriptor(current):
                raise NotImplementedError(self.__class__)
            # 9.c
            else:
                raise NotImplementedError(self.__class__)
        # 10
        elif is_data_descriptor(current) and is_data_descriptor(desc):
            # 10.a
            if current.configurable is False:
                # 10.a.i
                if current.writable is False and desc.writable is True:
                    return reject(throw, p)
                # 10.a.ii
                if current.writable is False:
                    if desc.has_set_value() and desc.value != current.value:
                        return reject(throw, p)
            # 10.b
            else:
                pass
        # 11
        elif is_accessor_descriptor(current) and is_accessor_descriptor(desc):
            # 11.a
            if current.configurable is False:
                # 11.a.i
                if desc.has_set_setter() and desc.setter != current.setter:
                    return reject(throw, p)
                # 11.a.ii
                if desc.has_set_getter() and desc.getter != current.getter:
                    return reject(throw, p)
        # 12
        prop = self._get_prop(p)
        prop.update_with_descriptor(desc)

        # 13
        return True

    ##########
    def to_boolean(self):
        return True

    def to_string(self):
        from obin.object.space import isfunc, isstr

        to_string = self.get(u'__tostring__')

        assert to_string.is_callable()
        assert isfunc(to_string)

        _str = to_string.Call(this=self)
        assert isstr(W_Primitive)
        return _str

    def to_object(self):
        return self

    def own_property_names(self):
        slotnames = self.slots.keys()
        return slotnames

    def available_property_names(self):
        names = self.own_property_names()
        for delegate in self.delegates():
            names += delegate.available_slot_names()

        return list(set(names))


class W_Globals(W_Object):
    pass

class W_BasicFunction(W_Object):
    _type_ = 'function'

    def Call(self, args=[], this=None, calling_context=None):
        raise NotImplementedError("abstract")

    def is_callable(self):
        return True

    def _to_string_(self):
        return u'function() {}'

class W_FunctionConstructor(W_BasicFunction):
    def _to_string_(self):
        return u'function Function() { [native code] }'

    # 15.3.2.1
    def Call(self, args=[], this=None, calling_context=None):
        arg_count = len(args)
        _args = u''
        body = u''
        if arg_count == 0:
            pass
        elif arg_count == 1:
            body = args[0].to_string()
        else:
            first_arg = args[0].to_string()
            _args = first_arg
            k = 2
            while k < arg_count:
                next_arg = args[k - 1].to_string()
                _args = _args + u',' + next_arg
                k = k + 1
            body = args[k - 1].to_string()

        src = u'function (' + _args + u') { ' + body + u' };'

        from obin.compile.astbuilder import parse_to_ast
        from obin.code import ast_to_bytecode

        ast = parse_to_ast(src)
        symbol_map = ast.symbol_map
        code = ast_to_bytecode(ast, symbol_map)
        # TODO hackish
        func = code.opcodes[0].funcobj

        from obin.object.space import object_space
        scope = object_space.get_global_environment()
        strict = func.strict
        params = func.params()
        w_func = object_space.new_func(func, formal_parameter_list=params, scope=scope, strict=strict)
        return w_func

# 15.7.2
class W_NumberConstructor(W_BasicFunction):
    # 15.7.1.1
    def Call(self, args=[], this=None, calling_context=None):
        from obin.object.space import _w, isnull_or_undefined, isundefined

        if len(args) >= 1 and not isnull_or_undefined(args[0]):
            return _w(args[0].ToNumber())
        elif len(args) >= 1 and isundefined(args[0]):
            return _w(NAN)
        else:
            return _w(0.0)

    def _to_string_(self):
        return u'function Number() { [native code] }'


class W_StringConstructor(W_BasicFunction):
    def Call(self, args=[], this=None, calling_context=None):
        from obin.builtins import get_arg
        from obin.object.space import _w
        arg0 = get_arg(args, 0, _w(u""))
        strval = arg0.to_string()
        return W_String(strval)

    def _to_string_(self):
        return u'function String() { [native code] }'

# 15.6.2
class W_BooleanConstructor(W_BasicFunction):
    def Call(self, args=[], this=None, calling_context=None):
        from obin.object.space import _w, isnull_or_undefined
        if len(args) >= 1 and not isnull_or_undefined(args[0]):
            boolval = args[0].to_boolean()
            return _w(boolval)
        else:
            return _w(False)

    def _to_string_(self):
        return u'function Boolean() { [native code] }'

# 15.9.2
class W_DateConstructor(W_BasicFunction):
    def Call(self, args=[], this=None, calling_context=None):
        import time
        from obin.object.space import _w, object_space
        value = _w(int(time.time() * 1000))
        obj = object_space.new_date(value)
        return obj

    def _to_string_(self):
        return u'function Date() { [native code] }'


# 15.4.2
class W_ArrayConstructor(W_BasicFunction):
    def __init__(self):
        from obin.object.space import _w
        W_BasicFunction.__init__(self)
        put_property(self, u'length', _w(1), writable=False, enumerable=False, configurable=False)

    def is_callable(self):
        return True

    def Call(self, args=[], this=None, calling_context=None):
        from obin.object.space import object_space, _w

        array = object_space.new_array()
        for index, obj in enumerate(args):
            array._idx_put(index, obj, False)
        return array


class W_Function(W_BasicFunction):
    _immutable_fields_ = ['_type_', '_class_', '_extensible_', '_scope_', '_params_[*]', '_strict_', '_function_']

    def __init__(self, function_body, formal_parameter_list=[], scope=None):
        W_BasicFunction.__init__(self)
        from obin.object.space import _w, newnull, object_space
        self._function_ = function_body
        self._scope_ = scope
        self._params_ = formal_parameter_list

        _len = len(formal_parameter_list)
        put_property(self, u'length', _w(_len), writable=False, enumerable=False, configurable=False)
        put_property(self, u'caller', newnull(), writable=True, enumerable=False, configurable=False)
        put_property(self, u'arguments', newnull(), writable=True, enumerable=False, configurable=False)

    def _to_string(self):
        return self._function_.to_string()

    def code(self):
        return self._function_

    def formal_parameters(self):
        return self._params_

    def Call(self, args=[], this=None, calling_context=None):
        from obin.runtime.execution_context import FunctionExecutionContext
        from obin.completion import Completion
        code = self.code()
        jit.promote(code)
        scope = self.scope()

        ctx = FunctionExecutionContext(code,
                                       argv=args,
                                       this=this,
                                       scope=scope,
                                       w_func=self)
        ctx._calling_context_ = calling_context
        res = code.run(ctx)

        assert isinstance(res, Completion)
        return res.value

    def scope(self):
        return self._scope_


class W_Date(W_Primitive):
    _type_ = 'Date'
    def __init__(self, value):
        self._value_ = value


class W_Boolean(W_Primitive):
    _type_ = 'boolean'
    _immutable_fields_ = ['_boolval_']

    def __init__(self, boolval):
        self._boolval_ = bool(boolval)

    def __str__(self):
        return 'W_Bool(%s)' % (str(self._boolval_), )

    def to_string(self):
        if self._boolval_ is True:
            return u'true'
        return u'false'

    def to_number(self):
        if self._boolval_ is True:
            return 1.0
        return 0.0

    def to_boolean(self):
        return self._boolval_


class W_String(W_Primitive):
    _type_ = 'string'
    _immutable_fields_ = ['_strval_']

    def __init__(self, strval):
        assert strval is not None and isinstance(strval, unicode)
        self._strval_ = strval

    def __eq__(self, other):
        other_string = other.to_string()
        return self.to_string() == other_string

    def __str__(self):
        return u'W_String("%s")' % (self._strval_)

    def ToObject(self):
        from obin.object.space import object_space
        return object_space.new_string(self)

    def to_string(self):
        return self._strval_

    def to_boolean(self):
        if len(self._strval_) == 0:
            return False
        else:
            return True

    def to_number(self):
        from obin.builtins.js_global import _strip
        from obin.runistr import encode_unicode_utf8
        from obin.constants import hex_rexp, oct_rexp, num_rexp

        u_strval = self._strval_

        u_strval = _strip(u_strval)
        s = encode_unicode_utf8(u_strval)

        if s == '':
            return 0.0

        match_data = num_rexp.match(s)
        if match_data is not None:
            num_lit = match_data.group()
            assert num_lit is not None
            assert isinstance(num_lit, str)

            if num_lit == 'Infinity' or num_lit == '+Infinity':
                return INFINITY
            elif num_lit == '-Infinity':
                return -INFINITY

            return float(num_lit)

        from obin.builtins.js_global import _parse_int

        match_data = hex_rexp.match(s)
        if match_data is not None:
            hex_lit = match_data.group(1)
            assert hex_lit is not None
            assert hex_lit.startswith('0x') is False
            assert hex_lit.startswith('0X') is False
            return float(_parse_int(unicode(hex_lit), 16))

        match_data = oct_rexp.match(s)
        if match_data is not None:
            oct_lit = match_data.group(1)
            assert oct_lit is not None
            return float(_parse_int(unicode(oct_lit), 8))

        return NAN


class W_Number(W_Primitive):
    """ Base class for numbers, both known to be floats
    and those known to be integers
    """
    _type_ = 'number'

    def to_boolean(self):
        num = self.to_number()
        if isnan(num):
            return False
        return bool(num)

    def __eq__(self, other):
        if isinstance(other, W_Number):
            return self.to_number() == other.to_number()
        else:
            return False

    def to_number(self):
        raise NotImplementedError

class W_IntNumber(W_Number):
    _immutable_fields_ = ['_intval_']

    """ Number known to be an integer
    """
    def __init__(self, intval):
        self._intval_ = intmask(intval)

    def __str__(self):
        return 'W_IntNumber(%s)' % (self._intval_,)

    def to_integer(self):
        return self._intval_

    def to_number(self):
        # XXX
        return float(self._intval_)

    def to_string(self):
        # XXX incomplete, this doesn't follow the 9.8.1 recommendation
        return unicode(str(self.to_integer()))

class W_FloatNumber(W_Number):
    _immutable_fields_ = ['_floatval_']

    """ Number known to be a float
    """
    def __init__(self, floatval):
        assert isinstance(floatval, float)
        self._floatval_ = floatval

    def __str__(self):
        return 'W_FloatNumber(%s)' % (self._floatval_,)

    def to_string(self):
        # XXX incomplete, this doesn't follow the 9.8.1 recommendation
        if isnan(self._floatval_):
            return u'NaN'
        if isinf(self._floatval_):
            if self._floatval_ > 0:
                return u'Infinity'
            else:
                return u'-Infinity'

        if self._floatval_ == 0:
            return u'0'

        res = u''
        try:
            res = unicode(formatd(self._floatval_, 'g', 10))
        except OverflowError:
            raise

        if len(res) > 3 and (res[-3] == '+' or res[-3] == '-') and res[-2] == '0':
            cut = len(res) - 2
            assert cut >= 0
            res = res[:cut] + res[-1]
        return res

    def to_number(self):
        return self._floatval_

    def to_integer(self):
        if isnan(self._floatval_):
            return 0

        if self._floatval_ == 0 or isinf(self._floatval_):
            return int(self._floatval_)

        return intmask(int(self._floatval_))


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


def put_property(obj, name, value, writable=False, configurable=False, enumerable=False, throw=False):
    descriptor = PropertyDescriptor(value=value, writable=writable, configurable=configurable, enumerable=enumerable)
    obj.define_own_property(name, descriptor, throw)
