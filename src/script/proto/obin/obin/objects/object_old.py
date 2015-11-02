__author__ = 'gloryofrobots'
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
