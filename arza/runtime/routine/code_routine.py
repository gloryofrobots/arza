from arza.compile.code.opcode import *
from arza.runtime import error
from arza.runtime.routine.base_routine import BaseRoutine
from arza.types import api, space, string, environment, datatype


class CodeRoutine(BaseRoutine):
    # _immutable_fields_ = ['_code_', '_name_', '_stack_size_', '_symbol_size_']
    BP = -1

    def __init__(self, func, stack, args, name, code, env):
        BaseRoutine.__init__(self, stack)

        assert space.issymbol(name)
        self._func_ = func
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

    def _on_resume(self, process, value):
        self.stack.push(value)

    def _on_activate(self):
        pass

    def _on_complete(self, process):
        pass

    def _print_code(self, opcode):
        api.d.pbp(self.BP, u"_____________________________")
        api.d.pbp(self.BP, u'%s %3d' % (opcode_info(self, opcode), self.pc))

    def _print_stack(self):
        api.d.pbp(self.BP, u"_________STACK______________")
        api.d.pbp(self.BP, self.stack.data[self.return_pointer:self.stack.pointer()])
        for s in self.stack.data[self.return_pointer:self.stack.pointer()]:
            api.d.pbp(self.BP, unicode(s))

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

            # api.d.pbp(self.BP, "_execute", opcode)
            # api.d.pbp(self.BP, "------ routine ----", api.to_s(self._name_), process)
            # self._print_stack()
            # self._print_code(opcode)
            # print(getattr(self, "_name_", None), str(hex(id(self))), d)
            self.pc += 1
            # *************************************
            if VOID == tag:
                stack.push(space.newvoid())
            # *************************************
            elif NIL == tag:
                stack.push(space.newnil())
            # *************************************
            elif FARGS == tag:
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
            elif DUP == tag:
                stack.push(stack.top())
            # *************************************
            elif POP == tag:
                stack.pop()
            # *************************************
            elif SWAP == tag:
                stack.swap()
            # *************************************
            elif LITERAL == tag:
                l = literals[arg1]
                stack.push(l)
            # *************************************
            elif LOCAL == tag:
                value = api.at_index(env, arg1)
                if space.isvoid(value):
                    literal = literals[arg2]
                    return error.throw_1(error.Errors.REFERENCE_ERROR, literal)

                stack.push(value)
            # *************************************
            elif OUTER == tag:
                assert arg1 > -1
                name = literals[arg2]
                value = env.ref(name, arg1)
                stack.push(value)
            # *************************************
            elif TEMPORARY == tag:
                _temp = env.temporary(arg1)
                if space.isvoid(_temp):
                    return error.throw_1(error.Errors.RUNTIME_ERROR,
                                         space.newstring(u"Internal error! Invalid temporary index %d" % arg1))
                stack.push(_temp)
            # *************************************
            elif IMPORT_NAME == tag:
                l = env.get_import(arg1)
                stack.push(l)
            # *************************************
            # STORING WITHOUT IDENTITY CHECK
            # USED IN DECORATORS
            elif STORE_LOCAL_VAR == tag:
                value = stack.top()
                api.put_at_index(env, arg1, value)
            # *************************************
            # TODO WHY NOT POP HERE? -- BECAUSE IT IS STATEMENT AND POP WILL BE GENERATED BY COMPILER
            elif STORE_LOCAL_CONST == tag:
                value = stack.top()
                if space.isvoid(value):
                    api.put_at_index(env, arg1, value)
                else:
                    val = api.at_index(env, arg1)
                    if not space.isvoid(val):
                        if not api.equal_b(val, value):
                            literal = literals[arg2]
                            error.throw_4(error.Errors.MATCH_ERROR,
                                          space.newstring(u"Variable has been already assigned in current scope"),
                                          literal, val, value)
                    else:
                        api.put_at_index(env, arg1, value)
            # *************************************
            elif STORE_TEMPORARY == tag:
                value = stack.top()
                env.set_temporary(arg1, value)
            # *************************************
            elif UNPACK_ARRAY == tag:
                seq = stack.pop()
                error.affirm_type(seq, space.isarray)
                seq_length = api.length_i(seq)
                if seq_length != arg1:
                    return error.throw_1(error.Errors.UNPACK_SEQUENCE_ERROR, seq)

                for i in range(seq_length - 1, -1, -1):
                    el = api.at_index(seq, i)
                    stack.push(el)
            # *************************************
            elif ARRAY == tag:
                tupl = stack.pop_n_array(arg1)
                stack.push(tupl)
            # *************************************
            elif METHOD_CALL == tag:
                func = stack.get_from_top(arg1)
                if not func.is_static:
                    args = stack.pop_n_array(arg1)
                    func = stack.pop()
                else:
                    args = stack.pop_n_array(arg1-1)
                    stack.pop()
                    func = stack.pop()

                res = api.call(process, func, args)
                if res is not None:
                    stack.push(res)

            # *************************************
            elif CALL == tag:
                func = stack.pop()
                args = stack.pop_n_array(arg1)
                # if arg1 < 0:
                #     args = space.newunit()
                # else:
                # args = space.newarguments(stack, stack.pointer(), arg1)
                #   print "ARGS-A", args.to_l()
                #   args = stack.pop_n_tuple(arg1)
                #
                # print "ARGS-T", args.to_l()
                res = api.call(process, func, args)
                if res is not None:
                    stack.push(res)
            # *************************************
            elif FSELF == tag:
                stack.push(self._func_)
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
            elif LOOKUP == tag:
                key = stack.pop()
                obj = stack.pop()
                val = api.lookup_symbol(process, obj, key)
                stack.push(val)
            # *************************************
            elif MAP == tag:
                args = []
                for _ in xrange(arg1):
                    name = stack.pop()
                    w_elem = stack.pop()
                    args.append(name)
                    args.append(w_elem)

                obj = space.newtable(args)
                stack.push(obj)
            # *************************************
            elif FUNCTION == tag:
                source = literals[arg1]
                w_func = space.newfunc_from_source(source, env)
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
            elif LABEL == tag:
                assert False, "Uncompiled label opcode"
            else:
                assert False, ("Unknown opcode", tag)

    def bytecode(self):
        return self._code_

    def __str__(self):
        return "<code_routine of %s>" % str(self._func_)
