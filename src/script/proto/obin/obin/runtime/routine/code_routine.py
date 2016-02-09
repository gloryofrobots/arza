from obin.compile.code.opcode import *
from obin.runtime import error
from obin.runtime.routine.base_routine import BaseRoutine
from obin.runtime.load import import_module
from obin.builtins.internals.internals import get_internal
from obin.types import api, space, string, environment
from obin.types.dispatch import generic


class CodeRoutine(BaseRoutine):
    # _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']

    def __init__(self, stack, args, name, code, env):
        BaseRoutine.__init__(self, stack)

        assert space.issymbol(name)
        self._code_ = code
        self._name_ = name
        self.args = args
        self.pc = 0
        self.result = None
        self.env = env

        self.catches = []


    def name(self):
        return self._name_

    def _info(self):
        info = self._code_.get_opcode_info(self.pc)
        if info is None:
            info_str = u""
            curline = u""
        else:
            info_str = u"{line = %d, column = %d}" % (api.to_i(info[1]), api.to_i(info[2]))
            curline = self._code_.info.get_line(api.to_i(info[1]))

        builder = string.Builder().add(self._name_).space().add_u(info_str).space() \
            .add_u(u"from: \"").add(self._code_.info.path).add_u(u"\"")
        if info is None:
            return builder.value()

        return builder.nl().space(8).add_u(curline).value()

    def _on_resume(self, value):
        self.stack.push(value)

    def _on_activate(self):
        pass

    def _on_complete(self, process):
        pass

    def _print_code(self, opcode):
        print u"_____________________________"
        print u'%s %3d' % (opcode_info(self, opcode), self.pc)

    def _catch(self, signal):
        assert self.is_suspended() or self.is_terminated()
        if len(self.catches) == 0:
            return False

        catch = self.catches.pop()
        self.pc = catch
        self.stack.push(signal)
        self._state = BaseRoutine.State.INPROCESS
        return True

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
            literals = env.literals
            # print "_execute", opcode
            # print "------ routine ----", api.to_s(self._name_)
            # self._print_stack()
            # self._print_code(opcode)
            # print(getattr(self, "_name_", None), str(hex(id(self))), d)
            self.pc += 1
            # *************************************
            if NIL == tag:
                stack.push(space.newnil())
            # *************************************
            elif ARGUMENTS == tag:
                stack.push(self.args)
            # *************************************
            elif RETURN == tag:
                self.complete(process, stack.top())
            # *************************************
            elif TRUE == tag:
                stack.push(space.newbool(True))
            # *************************************
            elif FALSE == tag:
                stack.push(space.newbool(False))
            # *************************************
            elif INTEGER == tag:
                stack.push(space.newint(arg1))
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
                value = api.at_index(env, arg1)
                if space.isnil(value):
                    literal = literals[arg2]
                    return error.throw_1(error.Errors.REFERENCE, literal)

                stack.push(value)
            # *************************************
            elif OUTER == tag:
                assert arg1 > -1

                name = literals[arg2]
                value = env.ref(name, arg1)
                # check for none value here too
                # for unbounded clojure vars X = 1 + func() -> 1 + X;
                if value is None:
                    literal = literals[arg2]
                    return error.throw_1(error.Errors.REFERENCE, literal)
                stack.push(value)
            # *************************************
            elif MEMBER == tag:
                name = stack.pop()
                obj = stack.pop()
                value = api.at(obj, name)
                stack.push(value)
            # *************************************
            # TODO WHY NOT POP HERE? -- BECAUSE IT IS STATEMENT AND POP WILL BE GENERATED BY COMPILER
            elif STORE_LOCAL == tag:
                value = stack.top()
                api.put_at_index(env, arg1, value)
            # *************************************
            elif STORE_MEMBER == tag:
                value = stack.pop()
                name = stack.pop()
                left = stack.pop()
                result = api.put(left, name, value)

                stack.push(result)
            # *************************************
            # TODO STORE_SYMBOL_MEMBER WITH LITERAL AS ARGUMENT
            # *************************************
            elif UNPACK_SEQUENCE == tag:
                seq = stack.pop()
                seq_length = api.n_length(seq)
                if seq_length != arg1:
                    return error.throw_1(error.Errors.UNPACK_SEQUENCE, seq)

                for i in range(seq_length - 1, -1, -1):
                    el = api.at_index(seq, i)
                    stack.push(el)
            # *************************************
            elif TUPLE == tag:
                tupl = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                stack.push(space.newtuple(tupl))
            # *************************************
            elif VECTOR == tag:
                lst = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                stack.push(space.newvector(lst))
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
                decision = api.to_b(value)
                if not decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_TRUE == tag:
                value = stack.pop()
                decision = api.to_b(value)
                if decision:
                    self.pc = arg1
            # *************************************
            elif JUMP_IF_FALSE_NOPOP == tag:
                value = stack.top()
                decision = api.to_b(value)
                if not decision:
                    self.pc = arg1
                else:
                    stack.pop()
            # *************************************
            elif JUMP_IF_TRUE_NOPOP == tag:
                value = stack.top()
                decision = api.to_b(value)
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
                value = api.to_b(iterator)
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
                # call is interrupted, probably co call
                if space.isinterrupt(next_el):
                    return
                stack.push(next_el)
            # *************************************
            elif MAP == tag:
                args = []
                for _ in xrange(arg1):
                    name = stack.pop()
                    w_elem = stack.pop()
                    args.append(name)
                    args.append(w_elem)

                obj = space.newpmap(args)
                stack.push(obj)
            # *************************************
            elif FUNCTION == tag:
                source = literals[arg1]
                w_func = space.newfunc(source.name, source.code, env)
                stack.push(w_func)
            # *************************************
            elif THROW == tag:
                val = stack.pop()
                self.terminate(val)
            # *************************************
            elif PUSH_CATCH == tag:
                self.catches.append(arg1)
            # *************************************
            elif POP_CATCH == tag:
                self.catches.pop()
            # *************************************
            elif LOAD == tag:
                name = literals[arg1]
                _module = import_module(process, name)
                stack.push(_module)
            # *************************************
            elif USE == tag:
                raise NotImplementedError()
            # *************************************
            elif MODULE == tag:
                _source = literals[arg1]
                _module = environment.create_environment(process, _source, env)
                stack.push(_module)
            # *************************************
            elif TRAIT == tag:
                name = literals[arg1]
                trait = space.newtrait(name)
                stack.push(trait)
            # *************************************
            elif GENERIC == tag:
                name = literals[arg1]
                trait = space.newgeneric(name)
                stack.push(trait)
            # *************************************
            elif SPECIFY == tag:
                methods = stack.pop_n(arg1)  # [:] # pop_n returns a non-resizable list
                methods = space.newtuple(methods)
                gen_fn = stack.top()
                generic.specify(process, gen_fn, methods)
            # *************************************
            elif LABEL == tag:
                assert False, "Uncompiled label opcode"
            else:
                assert False, "Unknown opcode"

    def bytecode(self):
        return self._code_
