from rpython.rlib.rarithmetic import intmask
from rpython.rlib import jit

from obin.objects.object_space import _w, isint
from obin.runtime.exception import ObinTypeError, ObinReferenceError
from obin.runtime.baseop import plus, sub, increment, decrement, mult, division, uminus, mod
from obin.objects.object import api
from obin.utils import tb

class Opcode(object):
    _settled_ = True
    _immutable_fields_ = ['_stack_change', 'funcobj']
    _stack_change = 1

    def __init__(self):
        pass

    def eval(self, ctx):
        """ Execute in context ctx
        """
        raise NotImplementedError

    def stack_change(self):
        return self._stack_change

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "%s: sc %s" % (self.__class__.__name__, str(self._stack_change))

class BaseBinaryComparison(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        s4 = ctx.stack_pop()
        s2 = ctx.stack_pop()
        res = self.decision(s2, s4)
        ctx.stack_append(res)

    def decision(self, op1, op2):
        raise NotImplementedError


class BaseBinaryBitwiseOp(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        s5 = ctx.stack_pop().value()()
        s6 = ctx.stack_pop().value()()
        ctx.stack_append(self.operation(ctx, s5, s6))

    def operation(self, ctx, op1, op2):
        raise NotImplementedError


class BaseBinaryOperation(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        right = ctx.stack_pop()
        left = ctx.stack_pop()
        ctx.stack_append(self.operation(ctx, left, right))


class BaseUnaryOperation(Opcode):
    _stack_change = 0


class LOAD_INTCONSTANT(Opcode):
    _immutable_fields_ = ['w_intvalue']

    def __init__(self, value):
        from obin.objects.object_space import newint
        self.w_intvalue = newint(int(value))

    def eval(self, ctx):
        ctx.stack_append(self.w_intvalue)

    def __str__(self):
        return 'LOAD_INTCONSTANT %s' % (self.w_intvalue.value(),)


class LOAD_BOOLCONSTANT(Opcode):
    _immutable_fields_ = ['w_boolval']

    def __init__(self, value):
        from obin.objects.object_space import newbool
        self.w_boolval = newbool(value)

    def eval(self, ctx):
        ctx.stack_append(self.w_boolval)

    def __str__(self):
        if self.w_boolval.to_boolean():
            return 'LOAD_BOOLCONSTANT true'
        return 'LOAD_BOOLCONSTANT false'


class LOAD_FLOATCONSTANT(Opcode):
    _immutable_fields_ = ['w_floatvalue']

    def __init__(self, value):
        from obin.objects.object_space import newfloat
        self.w_floatvalue = newfloat(float(value))

    def eval(self, ctx):
        ctx.stack_append(self.w_floatvalue)

    def __str__(self):
        return 'LOAD_FLOATCONSTANT %s' % (self.w_floatvalue.value(),)


class LOAD_STRINGCONSTANT(Opcode):
    _immutable_fields_ = ['w_strval']

    def __init__(self, value):
        from obin.objects.object_space import isstring
        assert isstring(value)
        self.w_strval = value

    def eval(self, ctx):
        w_strval = self.w_strval
        ctx.stack_append(w_strval)

    def __str__(self):
        return u'LOAD_STRINGCONSTANT "%s"' % (api.tostring(self.w_strval))


class LOAD_UNDEFINED(Opcode):
    def eval(self, ctx):
        from obin.objects.object_space import newundefined
        ctx.stack_append(newundefined())


class LOAD_NULL(Opcode):
    def eval(self, ctx):
        from obin.objects.object_space import newnull
        ctx.stack_append(newnull())


class LOAD_LOCAL(Opcode):
    _immutable_fields_ = ['identifier', 'index']

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    # 11.1.2
    def eval(self, ctx):
        # TODO put ref onto stack
        value = ctx.get_local(self.index)
        if value is None:
            raise ObinReferenceError(self.identifier)

        ctx.stack_append(value)

    def __str__(self):
        return 'LOAD_LOCAL %s (%d)' % (self.identifier, self.index)


class LOAD_OUTER(Opcode):
    _immutable_fields_ = ['identifier', 'index']

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

        assert self.index > -1

    # 11.1.2
    def eval(self, ctx):
        # TODO put ref onto stack
        value = ctx.get_ref(self.identifier, self.index)
        ctx.stack_append(value)

    def __str__(self):
        return 'LOAD_OUTER %s (%d)' % (self.identifier, self.index)


class LOAD_VECTOR(Opcode):
    _immutable_fields_ = ['counter']

    def __init__(self, counter):
        self.counter = counter

    @jit.unroll_safe
    def eval(self, ctx):
        from obin.objects.object_space import newvector
        array = newvector()

        list_w = ctx.stack_pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
        for el in list_w:
            array.append(el)
        ctx.stack_append(array)

    def stack_change(self):
        return -1 * self.counter + 1

    def __str__(self):
        return 'LOAD_VECTOR %d' % (self.counter,)



class LOAD_FUNCTION(Opcode):
    _immutable_fields_ = ['funcobj']

    def __init__(self, name, code):
        self.code = code
        self.name = name

    # 13.2 Creating Function Objects
    def eval(self, ctx):
        from obin.objects.object_space import newfunc

        scope = ctx.env()
        w_func = newfunc(self.name, self.code, scope)

        ctx.stack_append(w_func)

    def __repr__(self):
        return "\n%s\n**************\n%s\n******************\n" % (str(self.__class__), str(self.code))


class LOAD_OBJECT(Opcode):
    _immutable_fields_ = ["counter"]

    def __init__(self, count_items, count_traits):
        self.count_items = count_items
        self.count_traits = count_traits

    @jit.unroll_safe
    def eval(self, ctx):
        from obin.objects.object_space import newobject
        w_obj = newobject()
        for _ in range(self.count_items):
            name = ctx.stack_pop()
            w_elem = ctx.stack_pop()
            api.put(w_obj, name, w_elem)

        for _ in range(self.count_traits):
            trait = ctx.stack_pop()
            w_obj.isa(trait)

        ctx.stack_append(w_obj)

    #def __repr__(self):
        #return 'LOAD_OBJECT %d' % (self.counter,)


class LOAD_MEMBER(Opcode):
    _stack_change = -1

    def eval(self, ctx):
        w_obj = ctx.stack_pop()
        w_name = ctx.stack_pop()
        value = api.at(w_obj, w_name)

        ctx.stack_append(value)

    def __str__(self):
        return 'LOAD_MEMBER'


class LOAD_MEMBER_DOT(LOAD_MEMBER):
    def __str__(self):
        return 'LOAD_MEMBER_DOT'

    def eval(self, ctx):
        w_obj = ctx.stack_pop()
        w_name = ctx.stack_pop()
        value = api.lookup(w_obj, w_name)

        ctx.stack_append(value)


class COMMA(BaseUnaryOperation):
    def eval(self, ctx):
        one = ctx.stack_pop()
        ctx.stack_pop()
        ctx.stack_append(one)
        # XXX


class SUB(BaseBinaryOperation):
    def operation(self, ctx, left, right):
        return sub(ctx, left, right)


class IN(BaseBinaryOperation):
    def operation(self, ctx, left, right):
        from obin.objects.object_space import iscell
        if not iscell(right):
            raise ObinTypeError(u"TypeError: invalid object for in operator")  # + repr(right)
            
        return api.has(right, left)


# 11.4.3
def type_of(var):
    var_type = var.type()
    if var_type == 'null':
        return u'object'
    return unicode(var_type)


class ADD(BaseBinaryOperation):
    def operation(self, ctx, left, right):
        return plus(left, right)


class BITAND(BaseBinaryBitwiseOp):
    def operation(self, ctx, op1, op2):
        from obin.objects.object_space import newint
        return newint(int(op1 & op2))


class BITXOR(BaseBinaryBitwiseOp):
    def operation(self, ctx, op1, op2):
        from obin.objects.object_space import newint
        return newint(int(op1 ^ op2))


class BITOR(BaseBinaryBitwiseOp):
    def operation(self, ctx, op1, op2):
        from obin.objects.object_space import newint
        return newint(int(op1 | op2))


class BITNOT(BaseUnaryOperation):
    def eval(self, ctx):
        op = ctx.stack_pop().value()()
        from obin.objects.object_space import newint
        ctx.stack_append(newint(~op))


class URSH(BaseBinaryBitwiseOp):
    def eval(self, ctx):
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()

        rnum = rval.value()
        lnum = lval.value()

        #from rpython.rlib.rarithmetic import ovfcheck_float_to_int

        shift_count = rnum & 0x1F
        res = lnum >> shift_count
        w_res = _w(res)

        #try:
            #ovfcheck_float_to_int(res)
            #w_res = _w(res)
        #except OverflowError:
            #w_res = _w(float(res))

        ctx.stack_append(w_res)


class RSH(BaseBinaryBitwiseOp):
    def eval(self, ctx):
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()

        rnum = rval.value()
        lnum = lval.value()()
        shift_count = rnum & 0x1F
        res = lnum >> shift_count

        ctx.stack_append(_w(res))


class LSH(BaseBinaryBitwiseOp):
    def eval(self, ctx):
        from obin.objects.object import int32
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()

        lnum = lval.value()()
        rnum = rval.value()

        shift_count = intmask(rnum & 0x1F)
        res = int32(lnum << shift_count)

        ctx.stack_append(_w(res))


class MUL(BaseBinaryOperation):
    def operation(self, ctx, op1, op2):
        return mult(ctx, op1, op2)


class DIV(BaseBinaryOperation):
    def operation(self, ctx, op1, op2):
        return division(ctx, op1, op2)


class MOD(BaseBinaryOperation):
    def operation(self, ctx, op1, op2):
        return mod(ctx, op1, op2)


class UPLUS(BaseUnaryOperation):
    def eval(self, ctx):
        expr = ctx.stack_pop()
        res = None

        if isint(expr):
            res = expr
        else:
            num = expr.ToNumber()
            res = _w(num)

        ctx.stack_append(res)


class UMINUS(BaseUnaryOperation):
    def eval(self, ctx):
        ctx.stack_append(uminus(ctx.stack_pop(), ctx))


class NOT(BaseUnaryOperation):
    def eval(self, ctx):
        val = ctx.stack_pop()
        boolval = val.to_boolean()
        inv_boolval = not boolval
        ctx.stack_append(_w(inv_boolval))


class INCR(BaseUnaryOperation):
    def eval(self, ctx):
        value = ctx.stack_pop()
        if isint(value):
            num = value
        else:
            num = _w(value.ToNumber())
        newvalue = increment(num)
        ctx.stack_append(newvalue)


class DECR(BaseUnaryOperation):
    def eval(self, ctx):
        value = ctx.stack_pop()
        if isint(value):
            num = value
        else:
            num = _w(value.ToNumber())
        newvalue = decrement(ctx, num)
        ctx.stack_append(newvalue)


class GT(BaseBinaryComparison):
    def decision(self, op1, op2):
        from obin.runtime.baseop import compare_gt
        res = compare_gt(op1, op2)
        return res


class GE(BaseBinaryComparison):
    def decision(self, op1, op2):
        from obin.runtime.baseop import compare_ge
        res = compare_ge(op1, op2)
        return res


class LT(BaseBinaryComparison):
    def decision(self, op1, op2):
        from obin.runtime.baseop import compare_lt
        res = compare_lt(op1, op2)
        return res


class LE(BaseBinaryComparison):
    def decision(self, op1, op2):
        from obin.runtime.baseop import compare_le
        res = compare_le(op1, op2)
        return res


class EQ(BaseBinaryComparison):
    def decision(self, op1, op2):
        return api.equal(op1, op2)


class NE(BaseBinaryComparison):
    def decision(self, op1, op2):
        return not api.equal(op1, op2)


class IS(BaseBinaryComparison):
    def decision(self, op1, op2):
        return api.strict_equal(op1, op2)


class ISNOT(BaseBinaryComparison):
    def decision(self, op1, op2):
        return not api.strict_equal(op1, op2)

class STORE_MEMBER(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        left = ctx.stack_pop()
        name = ctx.stack_pop()
        value = ctx.stack_pop()
        api.put(left, name, value)

        ctx.stack_append(value)

class LOAD_PRIMITIVE(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, prim_id):
        self.prim_id = prim_id

    def eval(self, ctx):
        from obin.objects.object_space import object_space
        interpreter = object_space.interpreter
        primitive = interpreter.get_primitive(self.prim_id)
        ctx.stack_append(primitive)

    def __str__(self):
        return 'LOAD_PRIMITIVE %s ' % (self.prim_id)

class STORE_LOCAL(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    def eval(self, ctx):
        value = ctx.stack_top()
        ctx.store_local(self.index, value)

    def __str__(self):
        return 'STORE %s (%d)' % (self.identifier, self.index)

class STORE_OUTER(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    def eval(self, ctx):
        value = ctx.stack_top()
        ctx.store_ref(self.identifier, self.index, value)

    def __str__(self):
        return 'STORE %s (%d)' % (self.identifier, self.index)


class LABEL(Opcode):
    _stack_change = 0
    _immutable_fields_ = ['num']

    def __init__(self, num):
        self.num = num

    def __str__(self):
        return 'LABEL %d' % (self.num)

    #def __repr__(self):
        #return 'LABEL %d' % (self.num,)


class BaseJump(Opcode):
    _immutable_fields_ = ['where']
    _stack_change = 0

    def __init__(self, where):
        self.where = where
        self.decision = False

    def do_jump(self, ctx, pos):
        return 0

    #def __repr__(self):
        #return '%s %d' % (self.__class__.__name__, self.where)


class JUMP(BaseJump):
    def eval(self, ctx):
        pass

    def do_jump(self, ctx, pos):
        return self.where

    def __str__(self):
        return 'JUMP %d' % (self.where)


class BaseIfJump(BaseJump):
    def eval(self, ctx):
        value = ctx.stack_pop()

        self.decision = api.tobool(value).value()


class BaseIfNopopJump(BaseJump):
    def eval(self, ctx):
        value = ctx.stack_top()
        self.decision = api.tobool(value).value()


class JUMP_IF_FALSE(BaseIfJump):
    def do_jump(self, ctx, pos):
        if self.decision:
            return pos + 1
        return self.where

    def __str__(self):
        return 'JUMP_IF_FALSE %d' % (self.where)


class JUMP_IF_FALSE_NOPOP(BaseIfNopopJump):
    def do_jump(self, ctx, pos):
        if self.decision:
            ctx.stack_pop()
            return pos + 1
        return self.where

    def __str__(self):
        return 'JUMP_IF_FALSE_NOPOP %d' % (self.where)


class JUMP_IF_TRUE(BaseIfJump):
    def do_jump(self, ctx, pos):
        if self.decision:
            return self.where
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_TRUE %d' % (self.where)


class JUMP_IF_TRUE_NOPOP(BaseIfNopopJump):
    def do_jump(self, ctx, pos):
        if self.decision:
            return self.where
        ctx.stack_pop()
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_TRUE_NOPOP %d' % (self.where)


class RETURN(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        value = ctx.stack_top()
        ctx.routine().force_complete(value)


class POP(Opcode):
    _stack_change = -1

    def eval(self, ctx):
        ctx.stack_pop()

class LOAD_LIST(Opcode):
    _immutable_fields_ = ['counter']

    def __init__(self, counter):
        self.counter = counter

    def eval(self, ctx):
        # from obin.objects.object import W_List
        list_w = ctx.stack_pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
        from obin.objects.object_space import newvector
        ctx.stack_append(newvector(list_w))

    def stack_change(self):
        return -1 * self.counter + 1

    def __str__(self):
        return u'LOAD_LIST %d' % (self.counter,)


def load_arguments(ctx, counter):
    from obin.objects.object_space import newvector, isvector

    if counter == 0:
        return newvector([])
    # if counter == 1:
    #     args = ctx.stack_pop()
    #     # assert isvector(args)
    #     return args

    vectors = ctx.stack_pop_n(counter)  # [:] # pop_n returns a non-resizable list
    # vectors2 = []
    # ctx.stack_pop_n_into(counter, vectors2)  # [:] # pop_n returns a non-resizable list

    first = vectors[0]
    for i in xrange(1, len(vectors)):
        first.concat(vectors[i])

    return first


class CALL(Opcode):
    def __init__(self, counter):
        self.counter = counter

    def stack_change(self):
        return -1 * self.counter + 1

    def eval(self, ctx):
        func = ctx.stack_pop()
        argv = load_arguments(ctx, self.counter)

        api.call(func, ctx, argv)

    def __str__(self):
        return "CALL (%d)" % self.counter

    def __repr__(self):
        return self.__str__()

class CALL_METHOD(Opcode):
    _stack_change = -2

    def __init__(self, counter):
        self.counter = counter

    def stack_change(self):
        return -1 * self.counter + 1 + self._stack_change

    def eval(self, ctx):
        method = ctx.stack_pop()
        what = ctx.stack_pop()
        argv = load_arguments(ctx, self.counter)

        func = api.lookup(what, method)
        argv.prepend(what)

        api.call(func, ctx, argv)

    def __str__(self):
        return "CALL_METHOD (%d)" % self.counter

    def __repr__(self):
        return self.__str__()

class DUP(Opcode):
    def eval(self, ctx):
        ctx.stack_append(ctx.stack_top())

class THROW(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        val = ctx.stack_pop()
        ctx.routine().terminate(val)

class TRYCATCHBLOCK(Opcode):
    _immutable_fields_ = ['tryexec', 'catchexec', 'catchparam', 'finallyexec']

    def __init__(self, tryfunc, catchparam, catchfunc, finallyfunc):
        self.tryroutine = tryfunc
        self.catchroutine = catchfunc
        self.catchparam = catchparam
        self.finallyroutine = finallyfunc

    def stack_change(self):
        trystack = 0
        catchstack = 0
        finallystack = 0

        if self.tryroutine is not None:
            trystack = self.tryroutine.estimated_stack_size()
        #if self.catchexec is not None:
            #catchstack = self.catchexec.estimated_stack_size()
        if self.finallyroutine is not None:
            finallystack = self.finallyroutine.estimated_stack_size()

        return trystack + catchstack + finallystack

    def eval(self, ctx):
        from obin.runtime.context import BlockExecutionContext
        tryroutine = self.tryroutine.clone()
        catchroutine = self.catchroutine.clone()

        finallroutine = self.finallyroutine.clone() if self.finallyroutine else None
        parentroutine = ctx.routine()

        stack_p = ctx.stack_pointer()

        trycontext = BlockExecutionContext(tryroutine, ctx)
        tryroutine.add_signal_handler(None, catchroutine)
        catchcontext = BlockExecutionContext(catchroutine, ctx)
        continuation = None
        if finallroutine:
            finallycontext = BlockExecutionContext(finallroutine, ctx)
            # print "finallroutine.estimated_stack_size()", finallroutine.estimated_stack_size()
            # print finallroutine.code()

            continuation = finallroutine
            catchroutine.set_continuation(finallroutine)
            finallroutine.set_continuation(parentroutine)
        else:
            catchroutine.set_continuation(parentroutine)
            continuation = parentroutine

        catchroutine.set_start_stack_index(stack_p)
        ctx.routine().process.call_routine(tryroutine, continuation, parentroutine)



# ------------ iterator support ----------------
class LOAD_ITERATOR(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        obj = ctx.stack_pop()
        iterator = api.iterator(obj)
        ctx.stack_append(iterator)


class JUMP_IF_ITERATOR_EMPTY(BaseJump):
    def eval(self, ctx):
        pass

    def do_jump(self, ctx, pos):
        last_block_value = ctx.stack_pop()
        iterator = ctx.stack_top()
        if not iterator._tobool_():
            # discard the iterator
            ctx.stack_pop()
            # put the last block value on the stack
            ctx.stack_append(last_block_value)
            return self.where
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_ITERATOR_EMPTY %d' % (self.where)


class NEXT_ITERATOR(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        from obin.objects.object_space import isinterrupt
        iterator = ctx.stack_top()
        next_el = api.next(iterator)
        # call is interrupted, probably coroutine call
        if isinterrupt(next_el):
            return
        ctx.stack_append(next_el)


# ---------------- with support ---------------------


class WITH(Opcode):
    _immutable_fields_ = ['body']

    def __init__(self, body):
        self.body = body

    def eval(self, ctx):
        from obin.runtime.completion import is_return_completion
        from obin.runtime.context import WithExecutionContext
        # 12.10
        expr = ctx.stack_pop()
        expr_obj = expr.ToObject()

        with_ctx = WithExecutionContext(self.body, expr_obj, ctx)

        c = self.body.run(with_ctx)
        if is_return_completion(c):
            return c
        else:
            ctx.stack_append(c.value)

# ------------------ delete -------------------------

class DELETE_MEMBER(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        what = ctx.stack_pop().to_string()
        obj = ctx.stack_pop().ToObject()
        res = obj.delete(what)
        ctx.stack_append(_w(res))

# different opcode mappings, to make annotator happy

OpcodeMap = {}

for name, value in locals().items():
    if name.upper() == name and type(value) == type(Opcode) and issubclass(value, Opcode):
        OpcodeMap[name] = value


class Opcodes:
    pass

opcodes = Opcodes()
for name, value in OpcodeMap.items():
    setattr(opcodes, name, value)
