from obin.compile.code import *
from obin.runtime.exception import ObinReferenceError
from obin.runtime.reference import References
from obin.runtime.routine.base_routine import BaseRoutine
from obin.objects.stack import Stack
from obin.objects.space import (newbool, newundefined,
                                newnull, newvector, isinterrupt,
                                newobject, newfunc,
                                newint, newtuple, newgeneric, newtrait)
from obin.objects import api
from obin.runtime.load import import_module


def load_arguments(stack):
    length = stack.pop().value()
    elements = stack.pop_n(length)  # [:] # pop_n returns a non-resizable list
    # vectors2 = []
    # routine.stack.pop_n_into(counter, vectors2)  # [:] # pop_n returns a non-resizable list
    return newvector(elements)


class CodeRoutine(BaseRoutine):
    _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']

    def __init__(self, name, code, env):
        super(CodeRoutine, self).__init__()

        from obin.objects.space import isstring
        assert isstring(name)
        self._code_ = code

        self._name_ = name

        self.pc = 0
        self.result = None
        self.env = env

        scope = code.scope
        refs_size = scope.count_refs
        stack_size = code.estimated_stack_size
        self.literals = scope.literals
        if stack_size:
            self.stack = Stack(stack_size)
        else:
            self.stack = None
        if refs_size != 0:
            self.refs = References(env, refs_size)
        else:
            self.refs = None

    def name(self):
        return self._name_

    def _on_terminate(self, signal):
        self.__signal = signal

    def _on_resume(self, value):
        self.stack.push(value)

    def _on_activate(self):
        pass

    def _on_complete(self):
        pass

    def _execute(self):
        while True:
            if not self.is_inprocess():
                return
            opcode = self._code_.get_opcode(self.pc)
            tag = opcode[0]
            arg1 = opcode[1]
            arg2 = opcode[2]

            # d = u'%3d %25s %s ' % (self.pc, opcode_info(self, opcode), unicode([unicode(s) for s in self.stack]))
            # print(getattr(self, "_name_", None), str(hex(id(self))), d)
            self.pc += 1
            # *************************************
            if UNDEFINED == tag:
                self.stack.push(newundefined())
            # *************************************
            elif RETURN == tag:
                self.complete(self.stack.top())
            # *************************************
            elif NULL == tag:
                self.stack.push(newnull())
            # *************************************
            elif TRUE == tag:
                self.stack.push(newbool(True))
            # *************************************
            elif FALSE == tag:
                self.stack.push(newbool(False))
            # *************************************
            elif INTEGER == tag:
                self.stack.push(newint(arg1))
            # *************************************
            elif DUP == tag:
                self.stack.push(self.stack.top())
            # *************************************
            elif POP == tag:
                self.stack.pop()
            # *************************************
            elif LITERAL == tag:
                l = self.literals[arg1]
                self.stack.push(l)
            # *************************************
            elif LOCAL == tag:
                value = self.env.get_local(arg1)
                if value is None:
                    literal = self.literals[arg2]
                    raise ObinReferenceError(literal)

                self.stack.push(value)
            # *************************************
            elif OUTER == tag:
                assert arg1 > -1

                name = self.literals[arg2]
                value = self.refs.get_ref(name, arg1)
                self.stack.push(value)
            # *************************************
            elif MEMBER == tag:
                obj = self.stack.pop()
                name = self.stack.pop()
                value = api.at(obj, name)

                self.stack.push(value)
            # *************************************
            elif MEMBER_DOT == tag:
                obj = self.stack.pop()
                name = self.stack.pop()
                value = api.lookup(obj, name)

                self.stack.push(value)
            # *************************************
            # TODO WHY NOT POP HERE?
            elif STORE_LOCAL == tag:
                value = self.stack.top()
                self.env.set_local(arg1, value)
            # *************************************
            elif STORE_OUTER == tag:
                value = self.stack.top()
                literal = self.literals[arg2]
                self.refs.store_ref(literal, arg1, value)
            # *************************************
            elif STORE_MEMBER == tag:
                left = self.stack.pop()
                name = self.stack.pop()
                value = self.stack.pop()
                api.put(left, name, value)

                # TODO REMOVE PUSHING
                self.stack.push(value)
            # *************************************
            # TODO STORE_MEMBER_DOT
            # *************************************
            elif TUPLE == tag:
                tupl = self.stack.pop_n_to_tuple(arg1)  # [:] # pop_n returns a non-resizable list
                self.stack.push(newtuple(tupl))
            # *************************************
            elif VECTOR == tag:
                lst = self.stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                self.stack.push(newvector(lst))
            # *************************************
            elif CALL_PRIMITIVE == tag:
                prim = self.process.get_primitive(arg1)
                prim(self)
            # *************************************
            elif CALL == tag:
                func = self.stack.pop()
                argv = self.stack.pop()

                api.call(func, self, argv)
            # *************************************
            elif CALL_METHOD == tag:
                method = self.stack.pop()
                what = self.stack.pop()
                argv = self.stack.pop()

                func = api.lookup(what, method)
                # argv.prepend(what)

                api.call(func, self, argv)
            # *************************************
            elif CONCAT == tag:
                first = self.stack.pop()
                vec = self.stack.top()
                vec.concat(first)
            # *************************************
            elif PUSH_MANY == tag:
                args = self.stack.pop_n(arg1)
                vec = self.stack.top()
                vec.append_many(args)
            # *************************************
            elif JUMP == tag:
                self.pc = arg1
            # *************************************
            elif JUMP_IF_FALSE == tag:
                value = self.stack.pop()
                decision = api.toboolvalue(value)
                if not decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_TRUE == tag:
                value = self.stack.pop()
                decision = api.toboolvalue(value)
                if decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_FALSE_NOPOP == tag:
                value = self.stack.top()
                decision = api.toboolvalue(value)
                if not decision:
                    self.pc = arg1
                else:
                    self.stack.pop()
            # *************************************
            elif JUMP_IF_TRUE_NOPOP == tag:
                value = self.stack.top()
                decision = api.toboolvalue(value)
                if decision:
                    self.pc = arg1
                else:
                    self.stack.pop()
            # *************************************
            elif ITERATOR == tag:
                obj = self.stack.pop()
                iterator = api.iterator(obj)
                self.stack.push(iterator)
            # *************************************
            elif JUMP_IF_ITERATOR_EMPTY == tag:
                last_block_value = self.stack.pop()
                iterator = self.stack.top()
                value = api.toboolvalue(iterator)
                if not value:
                    # discard the iterator
                    self.stack.pop()
                    # put the last block value on the stack
                    self.stack.push(last_block_value)
                    self.pc = arg1
            # *************************************
            elif NEXT == tag:
                iterator = self.stack.top()
                next_el = api.next(iterator)
                # call is interrupted, probably coself call
                if isinterrupt(next_el):
                    return
                self.stack.push(next_el)
            # *************************************
            elif OBJECT == tag:
                obj = newobject()

                for _ in xrange(arg1):
                    name = self.stack.pop()
                    w_elem = self.stack.pop()
                    api.put(obj, name, w_elem)

                if arg2 > 0:
                    for _ in xrange(arg2):
                        trait = self.stack.pop()
                        obj.isa(trait)

                self.stack.push(obj)
            # *************************************
            elif FUNCTION == tag:
                w_func = newfunc(arg1, arg2, self.env)
                self.stack.push(w_func)
            # *************************************
            elif THROW == tag:
                val = self.stack.pop()
                self.terminate(val)
            # *************************************
            elif IMPORT == tag:
                name = self.literals[arg1]
                module = import_module(self.process, name)
                self.stack.push(module)
            # *************************************
            elif IMPORT_MEMBER == tag:
                name = self.literals[arg1]
                module = self.stack.top()
                member = api.lookup(module, name)
                self.stack.push(member)
            # *************************************
            elif TRAIT == tag:
                name = self.literals[arg1]
                trait = newtrait(name)
                self.stack.push(trait)
            # *************************************
            elif GENERIC == tag:
                name = self.literals[arg1]
                trait = newgeneric(name)
                self.stack.push(trait)
            # *************************************
            elif LABEL == tag:
                raise RuntimeError("Uncompiled label opcode")

    def bytecode(self):
        return self._code_
