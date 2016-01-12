from obin.compile.code import *
from obin.runtime.error import ObinReferenceError
from obin.runtime.reference import References
from obin.runtime.routine.base_routine import BaseRoutine
from obin.objects.space import (newbool, newundefined,
                                newnil, newvector, isinterrupt, isundefined,
                                newmap, newfunc,
                                newint, newtuple,
                                newgeneric, newtrait,
                                neworigin, newlist)
from obin.objects.types.dispatch.generic import specify
from obin.objects import api
from obin.runtime.load import import_module
from obin.builtins.internals.internals import get_internal


class CodeRoutine(BaseRoutine):
    # _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']

    def __init__(self, stack, args, name, code, env):
        BaseRoutine.__init__(self, stack)

        from obin.objects.space import isstring
        assert isstring(name)
        self._code_ = code
        self._name_ = name
        self.args = args
        self.pc = 0
        self.result = None
        self.env = env

        scope = code.scope
        refs_size = scope.count_refs
        self.literals = scope.literals
        if refs_size != 0:
            self.refs = References(env, refs_size)
        else:
            self.refs = None

    def name(self):
        return self._name_

    def _on_terminate(self, signal):
        pass

    def _on_resume(self, value):
        self.stack.push(value)

    def _on_activate(self):
        pass

    def _on_complete(self, process):
        pass

    def _print_code(self, opcode):
        print u"_____________________________"
        print u'%s %3d' % (opcode_info(self, opcode), self.pc)

    def _execute(self, process):
        while True:
            if not self.is_inprocess():
                return

            opcode = self._code_.get_opcode(self.pc)
            tag = opcode[0]
            arg1 = opcode[1]
            arg2 = opcode[2]
            stack = self.stack
            env = self.env
            literals = self.literals
            refs = self.refs
            # print "_execute", opcode
            # print "------ routine ----", api.to_native_string(self._name_)
            # self._print_stack()
            # self._print_code(opcode)
            # print(getattr(self, "_name_", None), str(hex(id(self))), d)
            self.pc += 1
            # *************************************
            if UNDEFINED == tag:
                stack.push(newundefined())
            # *************************************
            elif ARGUMENTS == tag:
                stack.push(self.args)
            # *************************************
            elif RETURN == tag:
                self.complete(process, stack.top())
            # *************************************
            elif NULL == tag:
                stack.push(newnil())
            # *************************************
            elif TRUE == tag:
                stack.push(newbool(True))
            # *************************************
            elif FALSE == tag:
                stack.push(newbool(False))
            # *************************************
            elif INTEGER == tag:
                stack.push(newint(arg1))
            # *************************************
            elif DUP == tag:
                stack.push(stack.top())
            # *************************************
            elif POP == tag:
                stack.pop()
            # *************************************
            elif LITERAL == tag:
                l = literals[arg1]
                stack.push(l)
            # *************************************
            elif LOCAL == tag:
                value = env.get_local(arg1)
                if isundefined(value):
                    literal = literals[arg2]
                    raise ObinReferenceError(literal)

                stack.push(value)
            # *************************************
            elif OUTER == tag:
                assert arg1 > -1

                name = literals[arg2]
                value = refs.get_ref(name, arg1)
                # check for none value here too
                # for unbounded clojure vars X = 1 + fn() { 1 + X }
                if value is None:
                    literal = literals[arg2]
                    raise ObinReferenceError(literal)
                stack.push(value)
            # *************************************
            elif MEMBER == tag:
                name = stack.pop()
                obj = stack.pop()
                value = api.at(obj, name)
                stack.push(value)
            # *************************************
            # TODO WHY NOT POP HERE?
            elif STORE_LOCAL == tag:
                value = stack.top()
                env.set_local(arg1, value)
            # *************************************
            elif STORE_OUTER == tag:
                value = stack.top()
                literal = literals[arg2]
                refs.store_ref(literal, arg1, value)
            # *************************************
            elif STORE_MEMBER == tag:
                left = stack.pop()
                name = stack.pop()
                value = stack.pop()
                api.put(left, name, value)

                # TODO REMOVE PUSHING
                stack.push(value)
            # *************************************
            # TODO STORE_MEMBER_DOT
            # *************************************
            elif UNPACK_SEQUENCE == tag:
                seq = stack.pop()
                seq_length = api.n_length(seq)
                if seq_length != arg1:
                    raise RuntimeError("Unpack sequence error : wrong length")
                for i in range(seq_length - 1, -1, -1):
                    el = api.at_index(seq, i)
                    stack.push(el)
            # *************************************
            elif TUPLE == tag:
                tupl = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                stack.push(newtuple(tupl))
            # *************************************
            elif VECTOR == tag:
                lst = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                stack.push(newvector(lst))
            # *************************************
            elif LIST == tag:
                lst = stack.pop_n_list(arg1)  # [:] # pop_n returns a non-resizable list
                stack.push(lst)
            # *************************************
            elif CALL_INTERNAL == tag:
                internal = get_internal(arg1)
                internal(process, self)
            # *************************************
            elif CALL == tag:
                func = stack.pop()
                args = stack.pop_n_tuple(arg1)
                api.call(process, func, args)
            # *************************************
            elif CALL_METHOD == tag:
                method = stack.pop()
                what = stack.pop()

                args = stack.pop_n_tuple(arg1)
                func = api.at(what, method)
                # argv.prepend(what)

                api.call(process, func, args)
            # *************************************
            elif SLICE == tag:
                end = stack.pop()
                start = stack.pop()
                obj = stack.pop()
                v = api.slice(obj, start, end)
                stack.push(v)
            # *************************************
            elif JUMP == tag:
                self.pc = arg1
            # *************************************
            elif JUMP_IF_FALSE == tag:
                value = stack.pop()
                decision = api.to_native_bool(value)
                if not decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_TRUE == tag:
                value = stack.pop()
                decision = api.to_native_bool(value)
                if decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_FALSE_NOPOP == tag:
                value = stack.top()
                decision = api.to_native_bool(value)
                if not decision:
                    self.pc = arg1
                else:
                    stack.pop()
            # *************************************
            elif JUMP_IF_TRUE_NOPOP == tag:
                value = stack.top()
                decision = api.to_native_bool(value)
                if decision:
                    self.pc = arg1
                else:
                    stack.pop()
            # *************************************
            elif ITERATOR == tag:
                obj = stack.pop()
                iterator = api.iterator(obj)
                stack.push(iterator)
            # *************************************
            elif JUMP_IF_ITERATOR_EMPTY == tag:
                last_block_value = stack.pop()
                iterator = stack.top()
                value = api.to_native_bool(iterator)
                if not value:
                    # discard the iterator
                    stack.pop()
                    # put the last block value on the stack
                    stack.push(last_block_value)
                    self.pc = arg1
            # *************************************
            elif NEXT == tag:
                iterator = stack.top()
                next_el = api.next(iterator)
                # call is interrupted, probably coself call
                if isinterrupt(next_el):
                    return
                stack.push(next_el)
            # *************************************
            elif MAP == tag:
                obj = newmap()

                for _ in xrange(arg1):
                    name = stack.pop()
                    w_elem = stack.pop()
                    api.put(obj, name, w_elem)

                stack.push(obj)
            # *************************************
            elif FUNCTION == tag:
                source = literals[arg1]
                w_func = newfunc(source.name, source.code, env)
                stack.push(w_func)
            # *************************************
            elif ORIGIN == tag:
                source = literals[arg1]
                w_func = newfunc(source.name, source.code, env)
                w_origin = neworigin(w_func)
                stack.push(w_origin)
            # *************************************
            elif THROW == tag:
                val = stack.pop()
                self.terminate(val)
            # *************************************
            elif IMPORT == tag:
                name = literals[arg1]
                module = import_module(process, name)
                stack.push(module)
            # *************************************
            elif IMPORT_MEMBER == tag:
                name = literals[arg1]
                module = stack.top()
                member = api.at(module, name)
                stack.push(member)
            # *************************************
            elif TRAIT == tag:
                name = literals[arg1]
                trait = newtrait(name)
                stack.push(trait)
            # *************************************
            elif GENERIC == tag:
                name = literals[arg1]
                trait = newgeneric(name)
                stack.push(trait)
            # *************************************
            elif SPECIFY == tag:
                methods = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                methods = newtuple(methods)
                generic = stack.top()
                specify(process, generic, methods)
            # *************************************
            elif LABEL == tag:
                raise RuntimeError("Uncompiled label opcode")
            else:
                raise RuntimeError("Unknown opcode")

    def bytecode(self):
        return self._code_
