from obin.runtime.baseop import plus, sub, mult, division, uminus, mod, compare_gt, \
    compare_ge, compare_le, compare_lt
from rpython.rlib.rarithmetic import intmask
from rpython.rlib import jit

from obin.objects.space import _w, isint, newint, newbool
from obin.runtime.exception import ObinTypeError, ObinReferenceError
from obin.objects import api
from obin.utils import tb


def apply_binary_on_unboxed(routine, operation):
    right = routine.stack.pop().value()
    left = routine.stack.pop().value()
    routine.stack.push(operation(routine, left, right))


def apply_binary(routine, operation):
    right = routine.stack.pop()
    left = routine.stack.pop()
    routine.stack.push(operation(routine, left, right))


def apply_unary(routine, operation):
    val = routine.stack.pop()
    routine.stack.push(operation(routine, val))


def apply_unary_ob_unboxed(routine, operation):
    val = routine.stack.pop().value()
    routine.stack.push(operation(routine, val))


def primitive_IN(routine):
    def _in(routine, left, right):
        from obin.objects.space import iscell
        if not iscell(right):
            raise ObinTypeError(u"TypeError: invalid object for in operator")

        return api.has(right, left)

    apply_binary(routine, _in)


def primitive_SUB(routine):
    apply_binary(routine, sub)


def primitive_ADD(routine):
    apply_binary(routine, plus)


def primitive_MUL(routine):
    apply_binary(routine, mult)


def primitive_DIV(routine):
    apply_binary(routine, division)


def primitive_MOD(routine):
    apply_binary(routine, mod)


def primitive_BITAND(routine):
    def _bitand(r, op1, op2):
        return newint(int(op1 & op2))

    apply_binary(routine, _bitand)


def primitive_BITXOR(routine):
    def _bitxor(r, op1, op2):
        return newint(int(op1 ^ op2))

    apply_binary(routine, _bitxor)


def primitive_BITOR(routine):
    def _bitor(r, op1, op2):
        return newint(int(op1 | op2))

    apply_binary(routine, _bitor)


def primitive_BITNOT(routine):
    def bitnot(r, op):
        return newint(~op)

    apply_unary(routine, bitnot)


def primitive_URSH(routine):
    def ursh(r, lval, rval):
        rnum = rval.value()
        lnum = lval.value()

        # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

        shift_count = rnum & 0x1F
        res = lnum >> shift_count
        return _w(res)

    apply_binary(routine, ursh)


def primitive_RSH(routine):
    def rsh(r, lval, rval):
        rnum = rval.value()
        lnum = lval.value()

        # from rpython.rlib.rarithmetic import ovfcheck_float_to_int

        shift_count = rnum & 0x1F
        res = lnum >> shift_count
        return _w(res)

    apply_binary(routine, rsh)


def primitive_LSH(routine):
    def lsh(r, lval, rval):
        rnum = rval.value()
        lnum = lval.value()

        shift_count = intmask(rnum & 0x1F)
        res = lnum << shift_count

        return _w(res)

    apply_binary(routine, lsh)


def primitive_UPLUS(routine):
    def uplus(r, op1):
        assert isint(op1)
        return op1

    apply_unary(routine, uplus)


def primitive_UMINUS(routine):
    apply_unary(routine, uminus)


def primitive_NOT(routine):
    def _not(r, val):
        v = api.toboolvalue(val)
        return newbool(not v)

    apply_unary(routine, _not)


# class BaseBinaryComparison(Opcode):
#     _stack_change = 0
#
#     def eval(self, routine):
#         s4 = routine.stack.pop()
#         s2 = routine.stack.pop()
#         res = self.decision(s2, s4)
#         routine.stack.push(res)
#
#     def decision(self, op1, op2):
#         raise NotImplementedError

def primitive_GT(routine):
    apply_binary(routine, compare_gt)


def primitive_GE(routine):
    apply_binary(routine, compare_ge)


def primitive_LT(routine):
    apply_binary(routine, compare_lt)


def primitive_LE(routine):
    apply_binary(routine, compare_le)


def primitive_EQ(routine):
    def eq(r, op1, op2):
        return api.equal(op1, op2)

    apply_binary(routine, eq)


def primitive_NE(routine):
    def noteq(r, op1, op2):
        return not api.equal(op1, op2)

    apply_binary(routine, noteq)


def primitive_IS(routine):
    def _is(r, op1, op2):
        return api.strict_equal(op1, op2)

    apply_binary(routine, _is)


def primitive_ISNOT(routine):
    def _isnot(r, op1, op2):
        return not api.strict_equal(op1, op2)

    apply_binary(routine, _isnot)


def primitive_ISA(routine):
    def _isa(routine, left, right):
        left.isa(right)

    apply_binary(routine, _isa)
