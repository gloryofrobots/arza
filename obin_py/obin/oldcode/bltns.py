__author__ = 'gloryofrobots'
# @jit.elidable
# def sign(i):
#     if i > 0:
#         return 1
#     if i < 0:
#         return -1
#     return 0

# MASK_32 = (2 ** 32) - 1
# MASK_16 = (2 ** 16) - 1
#
# @enforceargs(int)
# @jit.elidable
# def int32(n):
#     if n & (1 << (32 - 1)):
#         res = n | ~MASK_32
#     else:
#         res = n & MASK_32
#
#     return res
#
#
# @enforceargs(int)
# @jit.elidable
# def uint32(n):
#     return n & MASK_32
#
#
# @enforceargs(int)
# @jit.elidable
# def uint16(n):
#     return n & MASK_16

#
# class W_FloatNumberOld(W_Number):
#     _immutable_fields_ = ['_floatval_']
#
#     """ Number known to be a float
#     """
#     def __init__(self, floatval):
#         assert isinstance(floatval, float)
#         self._floatval_ = floatval
#         W__PrimitiveObject.__init__(self)
#
#     def __str__(self):
#         return 'W_FloatNumber(%s)' % (self._floatval_,)
#
#     def to_string(self):
#         # XXX incomplete, this doesn't follow the 9.8.1 recommendation
#         if isnan(self._floatval_):
#             return u'NaN'
#         if isinf(self._floatval_):
#             if self._floatval_ > 0:
#                 return u'Infinity'
#             else:
#                 return u'-Infinity'
#
#         if self._floatval_ == 0:
#             return u'0'
#
#         res = u''
#         try:
#             res = unicode(formatd(self._floatval_, 'g', 10))
#         except OverflowError:
#             raise
#
#         if len(res) > 3 and (res[-3] == '+' or res[-3] == '-') and res[-2] == '0':
#             cut = len(res) - 2
#             assert cut >= 0
#             res = res[:cut] + res[-1]
#         return res
#
#     def ToNumber(self):
#         return self._floatval_
#
#     def ToInteger(self):
#         if isnan(self._floatval_):
#             return 0
#
#         if self._floatval_ == 0 or isinf(self._floatval_):
#             return int(self._floatval_)
#
#         return intmask(int(self._floatval_))
#
# class W_RootOld(object):
#     _settled_ = True
#     _immutable_fields_ = ['_type_']
#     _type_ = ''
#
#     def __str__(self):
#         return self.to_string()
#
#     def to_string(self):
#         return u''
#
#     def type(self):
#         return self._type_
#
#     def to_boolean(self):
#         return False
#
#     def ToPrimitive(self, hint=None):
#         return self
#
#     def ToObject(self):
#         raise JsTypeError(u'W_Root.ToObject')
#
#     def ToNumber(self):
#         return 0.0
#
#     def ToInteger(self):
#         num = self.ToNumber()
#         if num == NAN:
#             return 0
#         if num == INFINITY or num == -INFINITY:
#             raise Exception('dafuq?')
#             return 0
#
#         return int(num)
#
#     def ToInt32(self):
#         num = self.ToInteger()
#         #if num == NAN or num == INFINITY or num == -INFINITY:
#         #return 0
#
#         return int32(num)
#
#     def ToUInt32(self):
#         num = self.ToInteger()
#         #if num == NAN or num == INFINITY or num == -INFINITY:
#         #return 0
#         return uint32(num)
#
#     def ToInt16(self):
#         num = self.ToInteger()
#         #if num == NAN or num == INFINITY or num == -INFINITY or num == 0:
#         #return 0
#
#         return uint16(num)
#
#     def is_callable(self):
#         return False
#
#     def check_object_coercible(self):
#         pass
# class Slots(object):
#     def __init__(self):
#         self.property_values = None
#         self.property_bindings = None
#         self.index = 0
#
#     def to_dict(self):
#         m = {}
#         for n, v in self.property_bindings.items():
#             m[n] = self.property_values[v]
#
#         return m
#
#     def __str__(self):
#         return str(self.to_dict())
#         pass
#
#     def __repr__(self):
#         return self.__str__()
#
#     def __copy__(self):
#         from copy import copy
#         clone = Slots()
#         clone.property_values = copy(self.property_values)
#         clone.property_bindings = copy(self.property_bindings)
#         clone.index = self.index
#         return clone
#
#     def contains(self, name):
#         return name in self.property_bindings
#
#     def values(self):
#         return self.property_values
#
#     def length(self):
#         return len(self.property_values)
#
#     def keys(self):
#         return self.property_bindings.keys()
#
#     def get(self, name):
#         idx = self.get_index(name)
#         if idx is None:
#             return
#
#         return self.get_by_index(idx)
#
#     def get_index(self, name):
#         try:
#             idx = self.property_bindings[name]
#         except KeyError:
#             return None
#         return idx
#
#     def set_by_index(self, idx, value):
#         self.property_values[idx] = value
#
#     def get_by_index(self, idx):
#         return self.property_values[idx]
#
#     def set(self, name, value):
#         idx = self.get_index(name)
#         self.property_values[idx] = value
#
#     def add(self, name, value):
#         idx = self.get_index(name)
#         if idx is None:
#             idx = self.index
#             self.property_bindings[name] = idx
#             self.index += 1
#
#         if idx >= len(self.property_values):
#             self.property_values = self.property_values + ([None] * (1 + idx - len(self.property_values)))
#
#         self.property_values[idx] = value
#         return idx
#
#     def delete(self, name):
#         idx = self.get_index(name)
#         if idx is None:
#             return
#
#         assert idx >= 0
#         self.property_values = self.property_values[:idx] + self.property_values[idx + 1:]
#         del self.property_bindings[name]
# from rpython.rlib import jit
#
#

# def hide_on_translate(*args):
#     default = None
#
#     def _wrap(f):
#         def _wrapped_f(*args):
#             from rpython.rlib.objectmodel import we_are_translated
#             if not we_are_translated():
#                 return f(*args)
#
#             return default
#
#         return _wrapped_f
#
#     if len(args) == 1 and callable(args[0]):
#         return _wrap(args[0])
#     else:
#         default = args[0]
#         return _wrap
# from rpython.rlib import jit
#
# class Map(object):
#     NOT_FOUND = -1
#     _immutable_fields_ = ['index', 'back', 'name']
#
#     def __init__(self):
#         self.index = self.NOT_FOUND
#         self.forward_pointers = {}
#         self.back = None
#         self.name = None
#
#     def __repr__(self):
#         return "%(back)s, [%(index)d]:%(name)s" % \
#                {'back': repr(self.back), 'index': self.index, 'name': self.name}
#
#     def __eq__(self, other):
#         keys = self.keys()
#         for k in keys:
#             if self.lookup(k) != other.lookup(k):
#                 return False
#
#
#     @jit.elidable_promote("0")
#     def contains(self, name):
#         idx = self.lookup(name)
#         return self.not_found(idx) is False
#
#     @jit.elidable_promote("0")
#     def not_found(self, idx):
#         return idx == self.NOT_FOUND
#
#     @jit.elidable_promote("0")
#     def lookup(self, name):
#         from object_space import isstring
#         assert isstring(name)
#         node = self._find_node_with_name(name)
#         if node is not None:
#             return node.index
#         return self.NOT_FOUND
#
#     def _find_node_with_name(self, name):
#         if self.name == name:
#             return self
#         if self.back is not None:
#             return self.back._find_node_with_name(name)
#
#     def _key(self):
#         return (self.name)
#
#     def empty(self):
#         return True
#
#     @jit.elidable
#     def len(self):
#         return self.index + 1
#
#     @jit.elidable
#     def add(self, name):
#         assert self.lookup(name) == self.NOT_FOUND
#         node = self.forward_pointers.get((name), None)
#         if node is None:
#             node = MapNode(self, name)
#             self.forward_pointers[node._key()] = node
#         return node
#
#     @jit.elidable
#     def keys(self):
#         if self.name is None:
#             return []
#
#         k = [self.name]
#         if self.back is not None:
#             return self.back.keys() + k
#
#         return k
#
#     def delete(self, key):
#         return self
#
#
# class MapRoot(Map):
#     def __repr__(self):
#         return "[%(index)d]:%(name)s" % {'index': self.index, 'name': self.name}
#
#
# class MapNode(Map):
#     def __init__(self, back, name):
#         Map.__init__(self)
#         self.back = back
#         self.name = name
#         self.index = back.index + 1
#
#     @jit.elidable
#     def delete(self, name):
#         if self.name == name:
#             return self.back
#         else:
#             n = self.back.delete(name)
#             return n.add(self.name)
#
#     def empty(self):
#         return False
#
#
# ROOT_MAP = MapRoot()
#
#
# def new_map():
#     return ROOT_MAP
