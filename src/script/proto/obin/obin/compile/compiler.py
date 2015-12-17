__author__ = 'gloryofrobots'
from token_type import *
from tokens import token_type_to_str
from parser import *

from obin.compile.scope import Scope
from obin.objects import space as obs
from obin.runtime import primitives
from obin.compile.code.source import CodeSource
from obin.compile.code import *

def compile_error(node, message, args):
    error_message = "Compile Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message, args)

def string_unquote(string):
    s = string
    if s.startswith('"'):
        assert s.endswith('"')
    else:
        assert s.startswith("'")
        assert s.endswith("'")
    s = s[:-1]
    s = s[1:]

    return s

class Compiler(object):
    def __init__(self):
        self.funclists = []
        self.scopes = []
        self.sourcename = ""
        self.depth = -1

    def enter_scope(self):
        self.depth = self.depth + 1

        new_scope = Scope()
        self.scopes.append(new_scope)
        #print 'starting new scope %d' % (self.depth, )

    def is_modifiable_binding(self, name):
        scope = self.current_scope()
        if scope.get_local_index(name) is not None:
            return True
        if scope.has_outer(name):
            return True

        return False

    def declare_outer(self, symbol):
        scope = self.current_scope()
        if not scope.is_function_scope():
            compile_error(self.current_node, "Outer variables can be declared only inside functions", symbol)
        if scope.has_outer(symbol):
            compile_error(self.current_node, "Outer variable has already been declared", symbol)
        scope.add_outer(symbol)

    # def declare_symbol(self, symbol):
    #     assert obs.isstring(symbol)
    #     idx = self.scopes[-1].add_symbol(symbol)
    #     # print "SYMBOL", symbol, len(symbol), idx
    #     return idx

    def declare_arguments(self, args, varargs):
        self.current_scope().add_arguments(args, varargs)

    def declare_function_name(self, name):
        self.current_scope().add_function_name(name)

    def declare_reference(self, symbol):
        assert obs.isstring(symbol)
        scope = self.current_scope()
        idx = scope.get_reference(symbol)
        if idx is None:
            idx = scope.add_reference(symbol)
        return idx

    def declare_literal(self, literal):
        scope = self.current_scope()
        idx = scope.get_literal(literal)
        if idx is None:
            idx = scope.add_literal(literal)
        return idx

    def declare_local(self, symbol):
        scope = self.current_scope()
        idx = scope.get_local_index(symbol)
        if idx is not None:
            return idx

        idx = scope.add_local(symbol)
        assert idx is not None
        return idx

    def get_variable_index(self, name):
        """
            return var_index, is_local_variable
        """
        scope_id = 0
        for scope in reversed(self.scopes):
            idx = scope.get_local_index(name)
            if idx is not None:
                if scope_id == 0:
                    return idx, True
                else:
                    # TODO here can be optimisation where we can calculate number of scopes to find back variable
                    ref_id = self.declare_reference(name)
                    return ref_id, False
            scope_id += 1

        # compile_error(self.current_node, "Non reachable variable", name)
        # COMMENT ERROR BECAUSE OF LATER LINKING OF BUILTINS
        ref_id = self.declare_reference(name)
        return ref_id, False

    def declare_variable(self, symbol):
        """
            return var_index, is_local
        """

        scope = self.current_scope()
        if scope.has_outer(symbol):
            idx = self.declare_reference(symbol)
            return idx, False

        idx = self.declare_local(symbol)
        return idx, True

    def exit_scope(self):
        self.depth = self.depth - 1
        self.scopes.pop()
        #print 'closing scope, returning to %d' % (self.depth, )

    def current_scope(self):
        return self.scopes[-1]

    def set_sourcename(self, sourcename):
        self.stsourcename = sourcename  # XXX I should call this

    def compile(self, ast):
        code = CodeSource()
        self.enter_scope()
        self.declare_arguments(None, False)
        self._compile(code, ast)
        scope = self.current_scope()
        final_scope = scope.finalize()
        compiled_code = code.finalize_compilation(final_scope)
        return compiled_code

    def _compile(self, code, ast):
        if isinstance(ast, list):
            self._compile_nodes(code, ast)
        else:
            self._compile_node(code, ast)

    def _compile_nodes(self, bytecode, nodes):
        if len(nodes) > 1:

            for node in nodes[:-1]:
                self._compile_node(bytecode, node)
                # last = bytecode.opcodes[-1]
                # if not isinstance(last, POP):
                bytecode.emit_0(POP)

        if len(nodes) > 0:
            node = nodes[-1]
            self._compile_node(bytecode, node)

    def _compile_node(self, code, node):
        self.current_node = node
        t = node.type
        t_str = token_type_to_str(t).replace("TT_", "")
        compiler = getattr(self, "_compile_" + t_str)
        return compiler(code, node)


    def _compile_FLOAT(self, bytecode, node):
        value = float(node.value)
        idx = self.declare_literal(obs.newfloat(value))
        bytecode.emit_1(LOAD_LITERAL, idx)

    def _compile_INT(self, bytecode, node):
        value = int(node.value)
        idx = self.declare_literal(obs.newint(value))
        bytecode.emit_1(LOAD_LITERAL, idx)

    def _compile_TRUE(self, bytecode, node):
        bytecode.emit_0(LOAD_TRUE)

    def _compile_FALSE(self, bytecode, node):
        bytecode.emit_0(LOAD_FALSE)

    def _compile_NIL(self, bytecode, node):
        bytecode.emit_0(LOAD_NULL)

    def _compile_UNDEFINED(self, bytecode, node):
        bytecode.emit_0(LOAD_UNDEFINED)

    def _emit_string(self, bytecode, string):
        idx = self.declare_literal(string)
        bytecode.emit_1(LOAD_LITERAL, idx)

    def _compile_STR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        self._emit_string(bytecode,  obs.newstring(strval))

    def _compile_CHAR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval  = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        self._emit_string(bytecode, obs.newstring(strval))

    def _compile_OUTER(self, bytecode, node):
        name = obs.newstring(node.first().value)
        self.declare_outer(name)

    def compile_binary_primitive(self, code, node, name):
        self._compile(code, node.first())
        self._compile(code, node.second())
        code.emit_1(CALL_PRIMITIVE, name)

    def compile_unary_primitive(self, code, node, name):
        self._compile(code, node.first())
        code.emit_1(CALL_PRIMITIVE, name)

    def _compile_BITAND(self, code, node):
        self.compile_binary_primitive(code, node, primitives.BITAND)

    def _compile_BITOR(self, code, node):
        self.compile_binary_primitive(code, node, primitives.BITOR)

    def _compile_BITXOR(self, code, node):
        self.compile_binary_primitive(code, node, primitives.BITXOR)

    def _compile_ADD(self, code, node):
        if node.arity == 2:
            self.compile_binary_primitive(code, node, primitives.ADD)
        elif node.arity == 1:
            self.compile_unary_primitive(code, node, primitives.UPLUS)
        else:
            assert 0

    def _compile_MUL(self, code, node):
        self.compile_binary_primitive(code, node, primitives.MUL)

    def _compile_MOD(self, code, node):
        self.compile_binary_primitive(code, node, primitives.MOD)

    def _compile_DIV(self, code, node):
        self.compile_binary_primitive(code, node, primitives.DIV)

    def _compile_SUB(self, code, node):
        if node.arity == 2:
            self.compile_binary_primitive(code, node, primitives.SUB)
        elif node.arity == 1:
            self.compile_unary_primitive(code, node, primitives.UMINUS)
        else:
            assert 0

    def _compile_BITNOT(self, code, node):
        self.compile_unary_primitive(code, node, primitives.BITNOT)

    def _compile_NOT(self, code, node):
        self.compile_unary_primitive(code, node, primitives.NOT)

    def _compile_GE(self, code, node):
        self.compile_binary_primitive(code, node, primitives.GE)

    def _compile_GT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.GT)

    def _compile_LE(self, code, node):
        self.compile_binary_primitive(code, node, primitives.LE)

    def _compile_LT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.LT)

    def _compile_IS(self, code, node):
        self.compile_binary_primitive(code, node, primitives.IS)

    def _compile_ISNOT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.ISNOT)

    def _compile_IN(self, code, node):
        self.compile_binary_primitive(code, node, primitives.IN)

    def _compile_EQ(self, code, node):
        self.compile_binary_primitive(code, node, primitives.EQ)

    def _compile_NE(self, code, node):
        self.compile_binary_primitive(code, node, primitives.NE)

    def _compile_LSHIFT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.LSH)

    def _compile_RSHIFT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.RSH)

    def _compile_URSHIFT(self, code, node):
        self.compile_binary_primitive(code, node, primitives.URSH)

    def _compile_AND(self, bytecode, node):
        self._compile(bytecode, node.first())
        one = bytecode.prealocate_label()
        bytecode.emit_1(JUMP_IF_FALSE_NOPOP, one)
        self._compile(bytecode, node.second())
        bytecode.emit_1(LABEL, one)

    def _compile_OR(self, bytecode, node):
        self._compile(bytecode, node.first())
        one = bytecode.prealocate_label()
        bytecode.emit_1(JUMP_IF_TRUE_NOPOP, one)
        self._compile(bytecode, node.second())
        bytecode.emit_1(LABEL, one)

    def _compile_ASSIGN_DOT(self, bytecode, node):
        member = node.first()
        name = obs.newstring(member.second().value)

        obj = member.first()
        self._compile(bytecode, node.second())
        self._emit_string(bytecode, name)
        self._compile(bytecode, obj)
        bytecode.emit_0(STORE_MEMBER)

    def _emit_store(self, bytecode, name):
        index, is_local = self.declare_variable(name)
        name_index = self.declare_literal(name)
        if is_local:
            bytecode.emit_2(STORE_LOCAL, index, name_index)
        else:
            bytecode.emit_2(STORE_OUTER, index, name_index)

    def _compile_ASSIGN(self, bytecode, node):
        left = node.first()
        if left.type == TT_DOT:
            return self._compile_ASSIGN_DOT(bytecode, node)

        name = obs.newstring(left.value)
        # self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        self._emit_store(bytecode, name)

    def _compile_modify_assignment_dot_primitive(self, bytecode, node, operation):
        member = node.first()
        name = obs.newstring(member.second().value)

        obj = member.first()

        self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        bytecode.emit_1(CALL_PRIMITIVE, operation)

        # self._compile(bytecode, node.second())
        self._emit_string(bytecode, name)
        self._compile(bytecode, obj)
        bytecode.emit_0(STORE_MEMBER)
        pass

    def _compile_modify_assignment_primitive(self, bytecode, node, operation):
        left = node.first()
        if left.type == TT_DOT:
            return self._compile_modify_assignment_dot_primitive(bytecode, node, operation)

        name = obs.newstring(left.value)
        if not self.is_modifiable_binding(name):
            compile_error(node, "Unreachable variable", name)

        # self._compile(bytecode, left)
        self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        bytecode.emit_1(CALL_PRIMITIVE, operation)
        self._emit_store(bytecode, name)

    def _compile_ADD_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.ADD)

    def _compile_SUB_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.SUB)

    def _compile_MUL_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.MUL)

    def _compile_DIV_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.DIV)

    def _compile_MOD_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.MOD)

    def _compile_BITOR_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.BITOR)

    def _compile_BITAND_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.BITAND)

    def _compile_BITXOR_ASSIGN(self, code, node):
        self._compile_modify_assignment_primitive(code, node, primitives.BITXOR)

    def _compile_NAME(self, code, node):
        name = obs.newstring(node.value)

        index, is_local = self.get_variable_index(name)
        name_index = self.declare_literal(name)
        if is_local:
            code.emit_2(LOAD_LOCAL, index, name_index)
        else:
            code.emit_2(LOAD_OUTER, index, name_index)

    def _compile_RETURN(self, code, node):
        expr = node.first()
        if is_empty_node(expr):
            code.emit_0(LOAD_UNDEFINED)
        else:
            self._compile(code, expr)

        code.emit_0(RETURN)

    def _compile_RAISE(self, code, node):
        expr = node.first()
        if is_empty_node(expr):
            code.emit_0(LOAD_UNDEFINED)
        else:
            self._compile(code, expr)

        code.emit_0(THROW)

    def _compile_object(self, code, items, traits):
        for t in traits:
            self._compile(code, t)

        for c in items:
            key = c[0]
            value = c[1]

            self._compile(code, value)
            if key.type == TT_NAME:
                # in case of names in object literal we must convert them to strings
                self._emit_string(code, obs.newstring(key.value))
            else:
                self._compile(code, key)

        code.emit_2(LOAD_OBJECT, len(items), len(traits))

    def _compile_LCURLY(self, code, node):
        items = node.first()
        self._compile_object(code, items, [])

    def _compile_OBJECT_EXPRESSION(self, code, node):
        traits = node.first()
        items = node.second()
        self._compile_object(code, items, traits)

    def _compile_OBJECT(self, code, node):
        """
        compiles object statements
        """
        if node.arity == 2:
            return self._compile_OBJECT_EXPRESSION(code, node)

        name = node.first()
        traits = node.second()
        items = node.third()
        self._compile_object(code, items, traits)

        name = obs.newstring(name.value)
        index = self.declare_local(name)
        name_index = self.declare_literal(name)
        # self._compile(bytecode, node.first())
        code.emit_2(STORE_LOCAL, index, name_index)

    def _compile_LSQUARE(self, code, node):
        # lookup like a[0]
        if node.arity == 2:
            return self._compile_LSQUARE_LOOKUP(code, node)

        items = node.first()
        for c in items:
            self._compile(code, c)

        code.emit_1(LOAD_VECTOR, len(items))

    def _compile_BREAK(self, code, node):
        code.emit_0(LOAD_UNDEFINED)
        if not code.emit_break():
            compile_error(node, u"break outside loop", ())

    def _compile_CONTINUE(self, code, node):
        code.emit_0(LOAD_UNDEFINED)
        if not code.emit_continue():
            compile_error(node, u"continue outside loop", ())

    def _compile_fn_args_and_body(self, code, funcname, params, outers, body):
        self.enter_scope()

        if not is_empty_node(params):
            args = []
            for param in params[:-1]:
                args.append(obs.newstring(param.value))

            lastparam = params[-1]

            if lastparam.type == TT_ELLIPSIS:
                args.append(obs.newstring(lastparam.first().value))
                varargs = True
            else:
                args.append(obs.newstring(lastparam.value))
                varargs = False
        else:
            args = None
            varargs = False

        self.declare_arguments(args, varargs)

        if not is_empty_node(outers):
            for outer in outers:
                self.declare_outer(obs.newstring(outer.value))

        if not funcname.isempty():
            self.declare_function_name(funcname)

        funccode = CodeSource()
        self._compile(funccode, body)
        current_scope = self.current_scope()
        scope = current_scope.finalize()
        self.exit_scope()
        print "LOCALS:", str(scope.variables.keys())
        print "REFS:", str(scope.references)
        compiled_code = funccode.finalize_compilation(scope)
        print [str(c) for c in compiled_code.opcodes]
        print "-------------------------"

        code.emit_2(LOAD_FUNCTION, funcname, compiled_code)

    def _compile_FN_EXPRESSION(self, code, node):
        name = obs.newstring(u'')
        params = node.first()
        outers = node.second()
        body = node.third()
        self._compile_fn_args_and_body(code, name, params, outers, body)

    def _compile_FN(self, code, node):
        """
        compiles function statements
        """
        if node.arity == 3:
            return self._compile_FN_EXPRESSION(code, node)

        name = node.first()
        funcname = obs.newstring(name.value)

        index = self.declare_local(funcname)
        params = node.second()
        outers = node.third()
        body = node.fourth()
        self._compile_fn_args_and_body(code, funcname, params, outers, body)

        funcname_index = self.declare_literal(funcname)
        code.emit_2(STORE_LOCAL, index, funcname_index)

    def _compile_branch(self, bytecode, condition, body, endif):
        self._compile(bytecode, condition)
        end_body = bytecode.prealocate_label()
        bytecode.emit_1(JUMP_IF_FALSE, end_body)
        self._compile(bytecode, body)
        bytecode.emit_1(JUMP, endif)
        bytecode.emit_1(LABEL, end_body)

    def _compile_IF_TERNARY(self, code, node):
        condition = node.first()
        truebranch = node.second()
        falsebranch = node.third()
        endif = code.prealocate_label()
        self._compile_branch(code, condition, truebranch, endif)
        self._compile(code, falsebranch)
        code.emit_1(LABEL, endif)

    def _compile_IF(self, code, node):
        if node.arity == 3:
            return self._compile_IF_TERNARY(code, node)
        branches = node.first()

        endif = code.prealocate_label()

        for i in range(len(branches) - 1):
            branch = branches[i]
            self._compile_branch(code, branch[0], branch[1], endif)

        elsebranch = branches[-1]
        if is_empty_node(elsebranch):
            code.emit_0(LOAD_UNDEFINED)
        else:
            self._compile(code, elsebranch[1])

        code.emit_1(LABEL, endif)

    def _compile_FOR(self, bytecode, node):
        vars = node.first()
        name = obs.newstring(vars[0].value)

        source = node.second()
        body = node.third()
        self._compile(bytecode, source)
        bytecode.emit_0(LOAD_ITERATOR)
        # load the "last" iterations result
        bytecode.emit_0(LOAD_UNDEFINED)
        precond = bytecode.emit_startloop_label()
        bytecode.continue_at_label(precond)
        finish = bytecode.prealocate_endloop_label(False)
        # update = bytecode.prealocate_updateloop_label()

        bytecode.emit_1(JUMP_IF_ITERATOR_EMPTY, finish)

        # put next iterator value on stack
        bytecode.emit_0(NEXT_ITERATOR)

        index = self.declare_local(name)
        # self._compile_string(bytecode, name)
        name_index = self.declare_literal(name)
        bytecode.emit_2(STORE_LOCAL, index, name_index)
        bytecode.emit_0(POP)

        self._compile(bytecode, body)
        # bytecode.emit_updateloop_label(update)

        bytecode.emit_1(JUMP, precond)
        bytecode.emit_endloop_label(finish)

    def _compile_WHILE(self, bytecode, node):
        condition = node.first()
        body = node.second()
        bytecode.emit_0(LOAD_UNDEFINED)
        startlabel = bytecode.emit_startloop_label()
        bytecode.continue_at_label(startlabel)
        self._compile(bytecode, condition)
        endlabel = bytecode.prealocate_endloop_label()
        bytecode.emit_1(JUMP_IF_FALSE, endlabel)
        bytecode.emit_0(POP)
        self._compile(bytecode, body)
        bytecode.emit_1(JUMP, startlabel)
        bytecode.emit_endloop_label(endlabel)
        bytecode.done_continue()

    def _compile_DOT(self, code, node):
        name = obs.newstring(node.second().value)
        self._emit_string(code, name)
        obj = node.first()
        self._compile(code, obj)
        code.emit_0(LOAD_MEMBER_DOT)
        # TODO LITERAL HERE
        # self.declare_symbol(name)

    def _compile_ELLIPSIS(self, code, node):
        pass

    def _compile_LSQUARE_LOOKUP(self, code, node):
        expr = node.second()
        self._compile(code, expr)
        obj = node.first()
        self._compile(code, obj)
        code.emit_0(LOAD_MEMBER)

    def _compile_args_list(self, code, args):
        normal_args_count = 0
        first_args_inserted = False
        if len(args) == 0:
            code.emit_1(LOAD_VECTOR, 0)
            return

        for arg in args:
            if arg.type == TT_ELLIPSIS:
                if first_args_inserted:
                    if normal_args_count:
                        code.emit_1(PUSH_MANY, normal_args_count)

                    self._compile(code, arg.first())
                    code.emit_0(CONCAT)
                else:
                    if normal_args_count:
                        code.emit_1(LOAD_VECTOR, normal_args_count)
                        self._compile(code, arg.first())
                        code.emit_0(CONCAT)
                    else:
                        self._compile(code, arg.first())

                first_args_inserted = True
                normal_args_count = 0
            else:
                self._compile(code, arg)
                normal_args_count += 1

        if normal_args_count:
            if first_args_inserted:
                code.emit_1(PUSH_MANY, normal_args_count)
            else:
                code.emit_1(LOAD_VECTOR, normal_args_count)

    def _compile_LPAREN_MEMBER(self, bytecode, node):
        obj = node.first()
        method = node.second()
        name = obs.newstring(method.value)
        args = node.third()
        # print "_compile_LPAREN_MEMBER", obj, method, args

        self._compile_args_list(bytecode, args)

        self._compile(bytecode, obj)
        self._emit_string(bytecode, name)
        # TODO LITERAL HERE
        # self.declare_symbol(name)

        bytecode.emit_0(CALL_METHOD)

    def _compile_LPAREN(self, bytecode, node):
        if node.arity == 3:
            return self._compile_LPAREN_MEMBER(bytecode, node)

        func = node.first()
        args = node.second()

        # print "_compile_LPAREN", func, args

        self._compile_args_list(bytecode, args)

        self._compile(bytecode, func)

        bytecode.emit_0(CALL)

def testprogram():
    with open("program2.obn") as f:
        data = f.read()

    return data

def compile(txt):
    ast = parse_string(txt)
    # print ast
    compiler = Compiler()
    code = compiler.compile(ast)
    return code

def compile_module(name, txt):
    from obin.objects.space import newmodule
    code = compile(txt)
    module = newmodule(name, code)
    return module

def print_code(code):
    print [str(c) for c in code.opcodes]

def compile_and_print(txt):
    print_code(compile(txt))

def _check(val1, val2):
    print val1
    print val2
    if val1 != val2:
        print val1
        print val2
        raise RuntimeError("Not equal")



# compile_and_print("""
# fn f(x, y, z){ return x + y + z; }
# fn f2() {}
# """)

