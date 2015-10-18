# encoding: utf-8
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rfloat import isnan, isinf, NAN, formatd, INFINITY
from rpython.rlib.objectmodel import enforceargs
from rpython.rlib import jit, debug

from obin.objects.object_map import new_map
from obin.runtime.exception import JsTypeError, JsRangeError
from obin.utils import tb


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


def _get_from_desc(desc, this):
    from obin.objects.object_space import newundefined
    if desc is None:
        return newundefined()

    if is_data_descriptor(desc):
        return desc.value

    if desc.has_set_getter() is False:
        return newundefined()

    getter = desc.getter
    res = getter.Call(this=this)
    return res


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
        return self.to_string()

    def to_string(self):
        return u''

    def type(self):
        return self._type_

    def to_boolean(self):
        return False

    def ToPrimitive(self, hint=None):
        return self

    def ToObject(self):
        raise JsTypeError(u'W_Root.ToObject')

    def ToNumber(self):
        return 0.0

    def ToInteger(self):
        num = self.ToNumber()
        if num == NAN:
            return 0
        if num == INFINITY or num == -INFINITY:
            raise Exception('dafuq?')
            return 0

        return int(num)

    def ToInt32(self):
        num = self.ToInteger()
        #if num == NAN or num == INFINITY or num == -INFINITY:
            #return 0

        return int32(num)

    def ToUInt32(self):
        num = self.ToInteger()
        #if num == NAN or num == INFINITY or num == -INFINITY:
            #return 0
        return uint32(num)

    def ToInt16(self):
        num = self.ToInteger()
        #if num == NAN or num == INFINITY or num == -INFINITY or num == 0:
            #return 0

        return uint16(num)

    def is_callable(self):
        return False

    def check_object_coercible(self):
        pass


class W_Primitive(W_Root):
    pass


class W_Undefined(W_Primitive):
    _type_ = 'undefined'

    def ToInteger(self):
        return 0

    def ToNumber(self):
        return NAN

    def to_string(self):
        return unicode(self._type_)

    def check_object_coercible(self):
        raise JsTypeError(u'W_Undefined.check_object_coercible')

    def ToObject(self):
        raise JsTypeError(u'W_Undefined.ToObject')


class W_Null(W_Primitive):
    _type_ = 'null'

    def to_boolean(self):
        return False

    def to_string(self):
        return u'null'

    def check_object_coercible(self):
        raise JsTypeError(u'W_Null.check_object_coercible')

    def ToObject(self):
        raise JsTypeError(u'W_Null.ToObject')

def reject(throw, msg=u''):
    if throw:
        raise JsTypeError(msg)
    return False


def _ireject(throw, idx):
    if throw:
        raise JsTypeError(unicode(str(idx)))
    return False


class W_Cell(W_Root):
    _type_ = 'object'
    _class_ = 'Object'
    _extensible_ = True
    _immutable_fields_ = ['_type_', '_class_']

    def __init__(self):
        from obin.objects.datastructs import Slots
        self._slots = Slots()

    def __str__(self):
        return "%s: %s" % (object.__repr__(self), self.klass())

    ##########
    # 8.6.2 Object Internal Properties and Methods
    def klass(self):
        return self._class_

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


class W_BasicObject(W_Cell):
    def __init__(self):
        W_Cell.__init__(self)
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

class W__PrimitiveObject(W_BasicObject):
    pass

class W_Boolean(W__PrimitiveObject):
    _type_ = 'boolean'
    _immutable_fields_ = ['_boolval_']

    def __init__(self, boolval):
        self._boolval_ = bool(boolval)
        W__PrimitiveObject.__init__(self)

    def __str__(self):
        return 'W_Bool(%s)' % (str(self._boolval_), )

    def prototype(self):
        from obin.objects.object_space import object_space, isnull
        if isnull(self._prototype_):
            self._prototype_ = object_space.proto_boolean
        return self._prototype_

    def to_string(self):
        if self._boolval_ is True:
            return u'true'
        return u'false'

    def ToNumber(self):
        if self._boolval_ is True:
            return 1.0
        return 0.0

    def to_boolean(self):
        return self._boolval_


class W_String(W__PrimitiveObject):
    _type_ = 'string'
    _immutable_fields_ = ['_strval_']

    def __init__(self, strval):
        from obin.objects.object_space import newint
        assert strval is not None and isinstance(strval, unicode)
        W__PrimitiveObject.__init__(self)
        self._strval_ = strval
        length = len(strval)
        self.put(u'length', newint(length),)
        from obin.objects.object_space import object_space,isnull

    def prototype(self):
        from obin.objects.object_space import object_space
        return object_space.proto_string

    def __eq__(self, other):
        other_string = other.to_string()
        return self.to_string() == other_string

    def __str__(self):
        return u'W_String("%s")' % (self._strval_)

    def get_own_property(self, p):
        value = W__PrimitiveObject.get_own_property(self, p)
        if value:
            return value

        if not is_array_index(p):
            return None

        string = self.to_string()
        index = int(p)
        length = len(string)

        if length <= index:
            return None

        result_string = string[index]
        from obin.objects.object_space import _w
        return _w(result_string),

    def to_string(self):
        return self._strval_

    def to_boolean(self):
        if len(self._strval_) == 0:
            return False
        else:
            return True

    def ToNumber(self):
        from obin.builtins.global_functions import _strip
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

        from obin.builtins.global_functions import _parse_int

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


class W_Number(W__PrimitiveObject):
    """ Base class for numbers, both known to be floats
    and those known to be integers
    """
    _type_ = 'number'

    def to_boolean(self):
        num = self.ToNumber()
        if isnan(num):
            return False
        return bool(num)

    def prototype(self):
        from obin.objects.object_space import object_space, isnull
        if isnull(self._prototype_):
            self._prototype_ = object_space.proto_number
        return self._prototype_

    def __eq__(self, other):
        if isinstance(other, W_Number):
            return self.ToNumber() == other.ToNumber()
        else:
            return False


class W_IntNumber(W_Number):
    _immutable_fields_ = ['_intval_']

    """ Number known to be an integer
    """
    def __init__(self, intval):
        self._intval_ = intmask(intval)
        W__PrimitiveObject.__init__(self)

    def __str__(self):
        return 'W_IntNumber(%s)' % (self._intval_,)

    def ToInteger(self):
        return self._intval_

    def ToNumber(self):
        # XXX
        return float(self._intval_)

    def to_string(self):
        # XXX incomplete, this doesn't follow the 9.8.1 recommendation
        return unicode(str(self.ToInteger()))

MASK_32 = (2 ** 32) - 1
MASK_16 = (2 ** 16) - 1


@enforceargs(int)
@jit.elidable
def int32(n):
    if n & (1 << (32 - 1)):
        res = n | ~MASK_32
    else:
        res = n & MASK_32

    return res


@enforceargs(int)
@jit.elidable
def uint32(n):
    return n & MASK_32


@enforceargs(int)
@jit.elidable
def uint16(n):
    return n & MASK_16


class W_FloatNumber(W_Number):
    _immutable_fields_ = ['_floatval_']

    """ Number known to be a float
    """
    def __init__(self, floatval):
        assert isinstance(floatval, float)
        self._floatval_ = floatval
        W__PrimitiveObject.__init__(self)

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

    def ToNumber(self):
        return self._floatval_

    def ToInteger(self):
        if isnan(self._floatval_):
            return 0

        if self._floatval_ == 0 or isinf(self._floatval_):
            return int(self._floatval_)

        return intmask(int(self._floatval_))

class W__Object(W_BasicObject):
    pass


class W_ModuleObject(W__Object):
    _class_ = 'global'


class W_BasicFunction(W_BasicObject):
    _class_ = 'Function'
    _type_ = 'function'

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
    _immutable_fields_ = ['_type_', '_class_', '_extensible_', '_scope_', '_params_[*]', '_function_']

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
        put_property(self, u'arguments', newnull())

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


# 10.6
class W_Arguments(W__Object):
    _class_ = 'Arguments'

    @jit.unroll_safe
    def __init__(self, func, names, args, env):
        from obin.objects.object_space import _w
        W__Object.__init__(self)
        _len = len(args)
        put_property(self, u'length', _w(_len))

        from obin.objects.object_space import object_space, newundefined
        _map = object_space.new_obj()
        mapped_names = new_map()
        jit.promote(_len)
        indx = _len - 1
        while indx >= 0:
            val = args[indx]
            put_property(self, unicode(str(indx)), val)
            if indx < len(names):
                name = names[indx]
                if not mapped_names.contains(name):
                    mapped_names = mapped_names.add(name)
                    _map.put(unicode(str(indx)), newundefined())
            indx = indx - 1

        if not mapped_names.empty():
            self._paramenter_map_ = _map

        put_property(self, u'callee', _w(func))

    def to_string(self):
        return unicode(str(self._paramenter_map_ ))
def make_arg_getter(name, env):
    pass
    #code = u'return %s;' % (name)


def make_arg_setter(name, env):
    pass
    #param = u'%s_arg' % (name)
    #code = u'%s = %s;' % (name, param)

# 15.8
class W_Math(W__Object):
    _class_ = 'Math'



class W_List(W_Root):
    def __init__(self, values):
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


class W__Array(W_BasicObject):
    _class_ = 'Array'

    def __init__(self):
        W_BasicObject.__init__(self)
        self._items = []

    def append(self, item):
        self._items.append(item)

    def _add_prop(self, name, value):
        idx = make_array_index(name)
        if idx != NOT_ARRAY_INDEX:
            self._add_iprop(idx, value)
        else:
            W_BasicObject._add_prop(self, name, value)

    def _add_iprop(self, idx, value):
        assert isinstance(idx, int) or isinstance(idx, long)
        #if idx not in self._items:

        self._items[idx] = value

    def _get_prop(self, name):
        idx = make_array_index(name)
        if idx != NOT_ARRAY_INDEX:
            return self._get_iprop(idx)
        else:
            return W_BasicObject._get_prop(self, name)

    def _get_iprop(self, idx):
        assert isinstance(idx, int) or isinstance(idx, long)
        assert idx >= 0
        return self._items[idx]

    def _del_prop(self, name):
        idx = make_array_index(name)
        if idx != NOT_ARRAY_INDEX:
            self._del_iprop(idx)
        else:
            W_BasicObject._del_prop(self, name)

    def _del_iprop(self, idx):
        assert isinstance(idx, int)
        assert idx >= 0
        try:
            del self._items[idx]
        except KeyError:
            pass

    def length(self):
        return len(self._items)

    def _named_properties_dict(self):
        my_d = {}
        for i in range(self.length()):
            my_d[unicode(str(i))] = None

        return my_d

def put_property(obj, name, value):
    obj.put(name, value)
