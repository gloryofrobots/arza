from rpython.rlib.rarithmetic import intmask
from rpython.rlib import jit

from obin.objects.object_space import _w, isint
from obin.runtime.exception import JsTypeError
from obin.runtime.baseop import plus, sub, AbstractEC, StrictEC, increment, decrement, mult, division, uminus, mod
from obin.objects.object import put_property
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
        from obin.objects.object_space import newbool
        s4 = ctx.stack_pop()
        s2 = ctx.stack_pop()
        res = self.decision(s2, s4)
        ctx.stack_append(newbool(res))

    def decision(self, op1, op2):
        raise NotImplementedError


class BaseBinaryBitwiseOp(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        s5 = ctx.stack_pop().ToInt32()
        s6 = ctx.stack_pop().ToInt32()
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
        return 'LOAD_INTCONSTANT %s' % (self.w_intvalue.ToInteger(),)


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
        return 'LOAD_FLOATCONSTANT %s' % (self.w_floatvalue.ToNumber(),)


class LOAD_STRINGCONSTANT(Opcode):
    _immutable_fields_ = ['w_strval']

    def __init__(self, value):
        from obin.objects.object_space import newstring
        self.w_strval = newstring(value)

    def eval(self, ctx):
        w_strval = self.w_strval
        ctx.stack_append(w_strval)

    def __str__(self):
        return u'LOAD_STRINGCONSTANT "%s"' % (self.w_strval.to_string())


class LOAD_UNDEFINED(Opcode):
    def eval(self, ctx):
        from obin.objects.object_space import newundefined
        ctx.stack_append(newundefined())


class LOAD_NULL(Opcode):
    def eval(self, ctx):
        from obin.objects.object_space import newnull
        ctx.stack_append(newnull())


class LOAD_VARIABLE(Opcode):
    _immutable_fields_ = ['identifier', 'index']

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    # 11.1.2
    def eval(self, ctx):
        # TODO put ref onto stack
        ref = ctx.get_ref(self.identifier, self.index)
        value = ref.get_value()
        ctx.stack_append(value)

    def __str__(self):
        return 'LOAD_VARIABLE "%s" (%d)' % (self.identifier, self.index)


class LOAD_THIS(Opcode):
    # 11.1.1
    def eval(self, ctx):
        this = ctx.this_binding()
        ctx.stack_append(this)


class LOAD_ARRAY(Opcode):
    _immutable_fields_ = ['counter']

    def __init__(self, counter):
        self.counter = counter

    @jit.unroll_safe
    def eval(self, ctx):
        from obin.objects.object_space import object_space
        array = object_space.new_array()

        list_w = ctx.stack_pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
        for el in list_w:
            array.append(el)
        ctx.stack_append(array)

    def stack_change(self):
        return -1 * self.counter + 1

    def __str__(self):
        return 'LOAD_ARRAY %d' % (self.counter,)


# class LOAD_LIST(Opcode):
#     _immutable_fields_ = ['counter']
#
#     def __init__(self, counter):
#         self.counter = counter
#
#     def eval(self, ctx):
#         from obin.objects.object import W_List
#         list_w = ctx.stack_pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
#         ctx.stack_append(W_List(list_w))
#
#     def stack_change(self):
#         return -1 * self.counter + 1
#
#     def __str__(self):
#         return u'LOAD_LIST %d' % (self.counter,)


class LOAD_FUNCTION(Opcode):
    _immutable_fields_ = ['funcobj']

    def __init__(self, funcobj):
        self.funcobj = funcobj

    # 13.2 Creating Function Objects
    def eval(self, ctx):
        from obin.objects.object_space import object_space

        func = self.funcobj
        scope = ctx.lexical_environment()
        params = func.params()
        w_func = object_space.new_func(func, formal_parameter_list=params, scope=scope)

        ctx.stack_append(w_func)

    def __repr__(self):
        return "\n%s\n**************\n%s\n******************\n" % (str(self.__class__), str(self.funcobj))


class LOAD_OBJECT(Opcode):
    _immutable_fields_ = ["counter"]

    def __init__(self, counter):
        self.counter = counter

    @jit.unroll_safe
    def eval(self, ctx):
        from obin.objects.object_space import object_space
        w_obj = object_space.new_obj()
        for _ in range(self.counter):
            top = ctx.stack_pop()
            name = top.to_string()
            w_elem = ctx.stack_pop()
            put_property(w_obj, name, w_elem)
        ctx.stack_append(w_obj)

    #def __repr__(self):
        #return 'LOAD_OBJECT %d' % (self.counter,)


class LOAD_MEMBER(Opcode):
    _stack_change = -1

    def eval(self, ctx):
        w_obj = ctx.stack_pop().ToObject()
        w_name = ctx.stack_pop()
        value = w_obj.get(w_name)

        ctx.stack_append(value)

    def __str__(self):
        return 'LOAD_MEMBER'


class LOAD_MEMBER_DOT(LOAD_MEMBER):
    def __str__(self):
        return 'LOAD_MEMBER_DOT'


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
        from obin.objects.object import W_BasicObject
        from obin.objects.object_space import newbool
        if not isinstance(right, W_BasicObject):
            raise JsTypeError(u"TypeError: fffuuu!")  # + repr(right)
        name = left.to_string()
        has_name = right.has_property(name)
        return newbool(has_name)


# 11.4.3
def type_of(var):
    var_type = var.type()
    if var_type == 'null':
        return u'object'
    return unicode(var_type)


class TYPEOF(BaseUnaryOperation):
    def eval(self, ctx):
        var = ctx.stack_pop()
        var_type = type_of(var)
        ctx.stack_append(_w(var_type))


class TYPEOF_VARIABLE(Opcode):
    _immutable_fields_ = ['index', 'name']

    def __init__(self, index, name):
        self.index = index
        self.name = name

    def eval(self, ctx):
        from obin.objects.object_space import newstring
        ref = ctx.get_ref(self.name, self.index)
        if ref.is_unresolvable_reference():
            var_type = u'undefined'
        else:
            var = ref.get_value()
            var_type = type_of(var)

        w_string = newstring(var_type)
        ctx.stack_append(w_string)

    def __str__(self):
        return 'TYPEOF_VARIABLE %s' % (self.name)


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
        op = ctx.stack_pop().ToInt32()
        from obin.objects.object_space import newint
        ctx.stack_append(newint(~op))


class URSH(BaseBinaryBitwiseOp):
    def eval(self, ctx):
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()

        rnum = rval.ToUInt32()
        lnum = lval.ToUInt32()

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

        rnum = rval.ToUInt32()
        lnum = lval.ToInt32()
        shift_count = rnum & 0x1F
        res = lnum >> shift_count

        ctx.stack_append(_w(res))


class LSH(BaseBinaryBitwiseOp):
    def eval(self, ctx):
        from obin.objects.object import int32
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()

        lnum = lval.ToInt32()
        rnum = rval.ToUInt32()

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
        return AbstractEC(op1, op2)


class NE(BaseBinaryComparison):
    def decision(self, op1, op2):
        return not AbstractEC(op1, op2)


class IS(BaseBinaryComparison):
    def decision(self, op1, op2):
        return StrictEC(op1, op2)


class ISNOT(BaseBinaryComparison):
    def decision(self, op1, op2):
        return not StrictEC(op1, op2)


class STORE_MEMBER(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        left = ctx.stack_pop()
        w_name = ctx.stack_pop()

        value = ctx.stack_pop()

        l_obj = left.ToObject()
        l_obj.put(w_name, value)

        ctx.stack_append(value)


class STORE(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    def eval(self, ctx):
        value = ctx.stack_top()
        ref = ctx.store_ref(self.identifier, self.index, value)

    def __str__(self):
        return 'STORE "%s" (%d)' % (self.identifier, self.index)


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
        self.decision = value.to_boolean()


class BaseIfNopopJump(BaseJump):
    def eval(self, ctx):
        value = ctx.stack_top()
        self.decision = value.to_boolean()


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


def common_call(ctx, funcobj, args, this, identifyer):
    if not funcobj.is_callable():
        err = u"%s is not a callable (%s)" % (funcobj.to_string(), identifyer.to_string())
        raise JsTypeError(err)

    from obin.objects.object import W_List, W_BasicFunction
    assert isinstance(args, W_List)
    assert isinstance(funcobj, W_BasicFunction)

    argv = args.to_list()
    funcobj.Call(args=argv, this=this, calling_context=ctx)

def load_arguments(ctx, counter):
    from obin.objects.object import W_List
    args = ctx.stack_pop_n(counter)  # [:] # pop_n returns a non-resizable list
    return W_List(args)

class CALL(Opcode):
    def __init__(self, counter):
        self.counter = counter

    def stack_change(self):
        return -1 * self.counter + 1

    def eval(self, ctx):
        from obin.objects.object_space import newundefined
        r1 = ctx.stack_pop()
        args = load_arguments(ctx, self.counter)
        common_call(ctx, r1, args, newundefined(), r1)

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
        what = ctx.stack_pop().ToObject()
        args = load_arguments(ctx, self.counter)

        name = method.to_string()
        r1 = what.get(name)
        common_call(ctx, r1, args, what, method)

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
        from obin.runtime.exception import JsThrowException
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
        from obin.runtime.execution_context import BlockExecutionContext
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
        ctx.routine().fiber.call_routine(tryroutine, continuation, parentroutine)


def commonnew(ctx, obj, args):
    if not obj.is_callable():
        msg = u'%s is not a constructor' % (obj.to_string())
        raise JsTypeError(msg)

    tb("commonnew")
    from obin.objects.object import W_BasicFunction
    assert isinstance(obj, W_BasicFunction)
    res = obj.Construct(args=args)
    return res


class NEW(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        from obin.objects.object import W_List

        y = ctx.stack_pop()
        x = ctx.stack_pop()
        assert isinstance(y, W_List)
        args = y.to_list()
        res = commonnew(ctx, x, args)
        ctx.stack_append(res)


class NEW_NO_ARGS(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        x = ctx.stack_pop()
        res = commonnew(ctx, x, [])
        ctx.stack_append(res)

# ------------ iterator support ----------------

from rpython.rlib.listsort import make_timsort_class
TimSort = make_timsort_class()


class LOAD_ITERATOR(Opcode):
    _stack_change = 0

    # separate function because jit should trace eval but not iterator creation.
    def _make_iterator(self, obj):
        props = []
        properties = obj.named_properties()
        TimSort(properties).sort()

        for key in properties:
            props.append(_w(key))

        props.reverse()

        from obin.objects.object import W_Iterator
        iterator = W_Iterator(props)
        return iterator

    def eval(self, ctx):
        exper_value = ctx.stack_pop()
        obj = exper_value.ToObject()

        from obin.objects.object import W_BasicObject
        assert isinstance(obj, W_BasicObject)

        iterator = self._make_iterator(obj)

        ctx.stack_append(iterator)


class JUMP_IF_ITERATOR_EMPTY(BaseJump):
    def eval(self, ctx):
        pass

    def do_jump(self, ctx, pos):
        from obin.objects.object import W_Iterator
        last_block_value = ctx.stack_pop()
        iterator = ctx.stack_top()
        assert isinstance(iterator, W_Iterator)
        if iterator.empty():
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
        from obin.objects.object import W_Iterator

        iterator = ctx.stack_top()
        assert isinstance(iterator, W_Iterator)
        next_el = iterator.next()
        ctx.stack_append(next_el)

        #ref = ctx.get_ref(self.name)
        #ref.put_value(next_el)

# ---------------- with support ---------------------


class WITH(Opcode):
    _immutable_fields_ = ['body']

    def __init__(self, body):
        self.body = body

    def eval(self, ctx):
        from obin.runtime.completion import is_return_completion
        from obin.runtime.execution_context import WithExecutionContext
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


class DELETE(Opcode):
    _immutable_fields_ = ['name', 'index']

    def __init__(self, name, index):
        self.name = name
        self.index = index

    def eval(self, ctx):
        from obin.runtime.reference import Reference
        from obin.runtime.exception import JsSyntaxError

        # 11.4.1
        ref = ctx.get_ref(self.name, self.index)
        if not isinstance(ref, Reference):
            res = True
        if ref.is_unresolvable_reference():
            raise JsSyntaxError()
        if ref.is_property_reference():
            obj = ref.get_base().ToObject()
            res = obj.delete(ref.get_referenced_name())
        else:
            raise JsSyntaxError("Can`t delete variable binding")

        if res is True:
            ctx.forget_ref(self.name, self.index)

        ctx.stack_append(_w(res))


class DELETE_MEMBER(Opcode):
    _stack_change = 0

    def eval(self, ctx):
        what = ctx.stack_pop().to_string()
        obj = ctx.stack_pop().ToObject()
        res = obj.delete(what)
        ctx.stack_append(_w(res))


class INSTANCEOF(Opcode):
    def eval(self, ctx):
        rval = ctx.stack_pop()
        lval = ctx.stack_pop()
        from obin.objects.object import W_BasicObject
        if not isinstance(rval, W_BasicObject):
            raise JsTypeError(u'TypeError INSTANCEOF')
        res = rval.has_instance(lval)
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
