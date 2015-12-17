from rpython.rlib.rarithmetic import intmask
from rpython.rlib import jit

from obin.objects.space import _w, isint
from obin.runtime.exception import ObinTypeError, ObinReferenceError
from obin.objects.object import api
from obin.utils import tb

class Opcode(object):
    _settled_ = True
    _immutable_fields_ = ['_stack_change', 'funcobj']
    _stack_change = 1

    def __init__(self):
        pass

    def eval(self, routine):
        """ Execute in context routine
        """
        raise NotImplementedError

    def stack_change(self):
        return self._stack_change

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return "%s: sc %s" % (self.__class__.__name__, str(self._stack_change))


class LOAD_TRUE(Opcode):
    _stack_change = 1
    def eval(self, routine):
        from obin.objects.space import newbool
        routine.stack.push(newbool(True))

class LOAD_FALSE(Opcode):
    _stack_change = 1
    def eval(self, routine):
        from obin.objects.space import newbool
        routine.stack.push(newbool(False))


class LOAD_UNDEFINED(Opcode):
    _stack_change = 1
    def eval(self, routine):
        from obin.objects.space import newundefined
        routine.stack.push(newundefined())


class LOAD_NULL(Opcode):
    _stack_change = 1
    def eval(self, routine):
        from obin.objects.space import newnull
        routine.stack.push(newnull())


class LOAD_LOCAL(Opcode):
    _stack_change = 1
    _immutable_fields_ = ['identifier', 'index']

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    # 11.1.2
    def eval(self, routine):
        # TODO put ref onto stack
        value = routine.env.get_local(self.index)
        if value is None:
            raise ObinReferenceError(self.identifier)

        routine.stack.push(value)

    def __str__(self):
        return 'LOAD_LOCAL %s (%d)' % (self.identifier, self.index)


class LOAD_OUTER(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 1

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

        assert self.index > -1

    # 11.1.2
    def eval(self, routine):
        # TODO put ref onto stack
        value = routine.refs.get_ref(self.identifier, self.index)
        routine.stack.push(value)

    def __str__(self):
        return 'LOAD_OUTER %s (%d)' % (self.identifier, self.index)


class LOAD_VECTOR(Opcode):
    _immutable_fields_ = ['counter']

    def __init__(self, counter):
        self.counter = counter

    @jit.unroll_safe
    def eval(self, routine):
        from obin.objects.space import newvector
        array = newvector()

        list_w = routine.stack.pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
        for el in list_w:
            array.append(el)
        routine.stack.push(array)

    def stack_change(self):
        return -1 * self.counter + 1

    def __str__(self):
        return 'LOAD_VECTOR %d' % (self.counter,)


class LOAD_LITERAL(Opcode):
    _immutable_fields_ = ['index']
    _stack_change = 1

    def __init__(self, index):
        self.index = index

    # 13.2 Creating Function Objects
    def eval(self, routine):
        l = routine.literals[self.index]

        routine.stack.push(l)

    def __str__(self):
        return 'LOAD_LITERAL %d' % (self.index,)

class LOAD_FUNCTION(Opcode):
    _immutable_fields_ = ['funcobj']
    _stack_change = 1

    def __init__(self, name, code):
        self.code = code
        self.name = name

    # 13.2 Creating Function Objects
    def eval(self, routine):
        from obin.objects.space import newfunc

        w_func = newfunc(self.name, self.code, routine.env)

        routine.stack.push(w_func)

    def __repr__(self):
        return "\n%s\n**************\n%s\n******************\n" % (str(self.__class__), str(self.code))


class LOAD_OBJECT(Opcode):
    _immutable_fields_ = ["count_items", "count_traits"]

    def __init__(self, count_items, count_traits):
        self.count_items = count_items
        self.count_traits = count_traits

    def stack_change(self):
        return -1 * self.count_items + self.count_traits + 1

    @jit.unroll_safe
    def eval(self, routine):
        from obin.objects.space import newobject
        w_obj = newobject()
        for _ in range(self.count_items):
            name = routine.stack.pop()
            w_elem = routine.stack.pop()
            api.put(w_obj, name, w_elem)

        for _ in range(self.count_traits):
            trait = routine.stack.pop()
            w_obj.isa(trait)

        routine.stack.push(w_obj)

    def __str__(self):
        return 'LOAD_OBJECT %d %d' % (self.count_items, self.count_traits)


class LOAD_MEMBER(Opcode):
    _stack_change = -1

    def eval(self, routine):
        w_obj = routine.stack.pop()
        w_name = routine.stack.pop()
        value = api.at(w_obj, w_name)

        routine.stack.push(value)

    def __str__(self):
        return 'LOAD_MEMBER'


class LOAD_MEMBER_DOT(LOAD_MEMBER):
    def __str__(self):
        return 'LOAD_MEMBER_DOT'

    def eval(self, routine):
        w_obj = routine.stack.pop()
        w_name = routine.stack.pop()
        value = api.lookup(w_obj, w_name)

        routine.stack.push(value)


class STORE_MEMBER(Opcode):
    _stack_change = -2

    def eval(self, routine):
        left = routine.stack.pop()
        name = routine.stack.pop()
        value = routine.stack.pop()
        api.put(left, name, value)

        # TODO REMOVE PUSHING
        routine.stack.push(value)

# TODO FIX STACK CHANGE
class CALL_PRIMITIVE(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, prim_id):
        self.prim_id = prim_id

    def eval(self, routine):

        prim = routine.process.get_primitive(self.prim_id)
        prim(routine)

    def __str__(self):
        from obin.runtime.primitives import primitive_to_str
        return 'CALL_PRIMITIVE %s ' % (primitive_to_str(self.prim_id))

class STORE_LOCAL(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    def eval(self, routine):
        value = routine.stack.top()
        routine.env.set_local(self.index, value)

    def __str__(self):
        return 'STORE %s (%d)' % (self.identifier, self.index)

class STORE_OUTER(Opcode):
    _immutable_fields_ = ['identifier', 'index']
    _stack_change = 0

    def __init__(self, index, identifier):
        assert index is not None
        self.index = index
        self.identifier = identifier

    def eval(self, routine):
        value = routine.stack.top()
        routine.refs.store_ref(self.identifier, self.index, value)

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

    def do_jump(self, routine, pos):
        return 0

    #def __repr__(self):
        #return '%s %d' % (self.__class__.__name__, self.where)


class JUMP(BaseJump):
    _stack_change = 0
    def eval(self, routine):
        pass

    def do_jump(self, routine, pos):
        return self.where

    def __str__(self):
        return 'JUMP %d' % (self.where)


class BaseIfJump(BaseJump):
    _stack_change = 0
    def eval(self, routine):
        value = routine.stack.pop()

        self.decision = api.toboolvalue(value)


class BaseIfNopopJump(BaseJump):
    _stack_change = 0
    def eval(self, routine):
        value = routine.stack.top()
        self.decision = api.toboolvalue(value)


class JUMP_IF_FALSE(BaseIfJump):
    _stack_change = 0
    def do_jump(self, routine, pos):
        if self.decision:
            return pos + 1
        return self.where

    def __str__(self):
        return 'JUMP_IF_FALSE %d' % (self.where)


class JUMP_IF_FALSE_NOPOP(BaseIfNopopJump):
    _stack_change = 0
    def do_jump(self, routine, pos):
        if self.decision:
            routine.stack.pop()
            return pos + 1
        return self.where

    def __str__(self):
        return 'JUMP_IF_FALSE_NOPOP %d' % (self.where)


class JUMP_IF_TRUE(BaseIfJump):
    _stack_change = 0
    def do_jump(self, routine, pos):
        if self.decision:
            return self.where
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_TRUE %d' % (self.where)


class JUMP_IF_TRUE_NOPOP(BaseIfNopopJump):
    _stack_change = 0
    def do_jump(self, routine, pos):
        if self.decision:
            return self.where
        routine.stack.pop()
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_TRUE_NOPOP %d' % (self.where)

class RETURN(Opcode):
    _stack_change = 0

    def eval(self, routine):
        value = routine.stack.top()
        routine.complete(value)


class POP(Opcode):
    _stack_change = -1

    def eval(self, routine):
        routine.stack.pop()

class LOAD_LIST(Opcode):
    _immutable_fields_ = ['counter']

    def __init__(self, counter):
        self.counter = counter

    def eval(self, routine):
        # from obin.objects.object import W_List
        list_w = routine.stack.pop_n(self.counter)  # [:] # pop_n returns a non-resizable list
        from obin.objects.space import newvector
        routine.stack.push(newvector(list_w))

    def stack_change(self):
        return -1 * self.counter + 1

    def __str__(self):
        return u'LOAD_LIST %d' % (self.counter,)


def load_arguments(routine, counter):
    from obin.objects.space import newvector, isvector

    if counter == 0:
        return newvector([])
    # if counter == 1:
    #     args = routine.stack.pop()
    #     # assert isvector(args)
    #     return args

    vectors = routine.stack.pop_n(counter)  # [:] # pop_n returns a non-resizable list
    # vectors2 = []
    # routine.stack.pop_n_into(counter, vectors2)  # [:] # pop_n returns a non-resizable list

    first = vectors[0]
    for i in xrange(1, len(vectors)):
        first.concat(vectors[i])

    return first


class CALL(Opcode):
    def __init__(self, counter):
        self.counter = counter

    def stack_change(self):
        return -1 * self.counter + 1

    def eval(self, routine):
        func = routine.stack.pop()
        argv = load_arguments(routine, self.counter)

        api.call(func, routine, argv)

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

    def eval(self, routine):
        method = routine.stack.pop()
        what = routine.stack.pop()
        argv = load_arguments(routine, self.counter)

        func = api.lookup(what, method)
        argv.prepend(what)

        api.call(func, routine, argv)

    def __str__(self):
        return "CALL_METHOD (%d)" % self.counter

    def __repr__(self):
        return self.__str__()

class DUP(Opcode):
    def eval(self, routine):
        routine.stack.push(routine.stack.top())

class THROW(Opcode):
    _stack_change = 0

    def eval(self, routine):
        val = routine.stack.pop()
        routine.terminate(val)

# ------------ iterator support ----------------
class LOAD_ITERATOR(Opcode):
    _stack_change = 0

    def eval(self, routine):
        obj = routine.stack.pop()
        iterator = api.iterator(obj)
        routine.stack.push(iterator)


class JUMP_IF_ITERATOR_EMPTY(BaseJump):
    def eval(self, routine):
        pass

    def do_jump(self, routine, pos):
        last_block_value = routine.stack.pop()
        iterator = routine.stack.top()
        if not iterator._tobool_():
            # discard the iterator
            routine.stack.pop()
            # put the last block value on the stack
            routine.stack.push(last_block_value)
            return self.where
        return pos + 1

    def __str__(self):
        return 'JUMP_IF_ITERATOR_EMPTY %d' % (self.where)

class NEXT_ITERATOR(Opcode):
    _stack_change = 0

    def eval(self, routine):
        from obin.objects.space import isinterrupt
        iterator = routine.stack.top()
        next_el = api.next(iterator)
        # call is interrupted, probably coroutine call
        if isinterrupt(next_el):
            return
        routine.stack.push(next_el)

OpcodeMap = {}

for name, value in locals().items():
    if name.upper() == name and type(value) == type(Opcode) and issubclass(value, Opcode):
        OpcodeMap[name] = value


class Opcodes:
    pass

opcodes = Opcodes()
for name, value in OpcodeMap.items():
    setattr(opcodes, name, value)
