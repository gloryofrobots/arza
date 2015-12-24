__author__ = 'gloryofrobots'
from obin.compile.parse.token_type import *
from obin.compile.parse.tokens import token_type_to_str
from obin.compile.parse.parser import *
from obin.compile.parse.node import is_empty_node, is_list_node, is_iterable_node
from obin.compile.scope import Scope
from obin.objects import space as obs
from obin.runtime import primitives
from obin.compile.code.source import CodeSource
from obin.compile.code import *
from obin.utils.builtins import is_absent_index


def compile_error(node, message):
    error_message = "Compile Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message)

def compile_error_1(node, message, arg):
    error_message = "Compile Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message, arg)


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


class Compiler:
    def __init__(self):
        self.funclists = []
        self.scopes = []
        self.sourcename = ""
        self.depth = -1

    def enter_scope(self):
        self.depth = self.depth + 1

        new_scope = Scope()
        self.scopes.append(new_scope)
        # print 'starting new scope %d' % (self.depth, )

    def is_modifiable_binding(self, name):
        scope = self.current_scope()
        if not is_absent_index(scope.get_local_index(name)):
            return True
        if scope.has_outer(name):
            return True

        return False

    def declare_outer(self, symbol):
        scope = self.current_scope()
        if not scope.is_function_scope():
            compile_error_1(self.current_node, "Outer variables can be declared only inside functions", symbol)
        if scope.has_outer(symbol):
            compile_error_1(self.current_node, "Outer variable has already been declared", symbol)
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
        if is_absent_index(idx):
            idx = scope.add_reference(symbol)
        return idx

    def declare_literal(self, literal):
        assert obs.isany(literal)
        scope = self.current_scope()
        idx = scope.get_literal(literal)
        if is_absent_index(idx):
            idx = scope.add_literal(literal)
        return idx

    def declare_local(self, symbol):
        scope = self.current_scope()
        idx = scope.get_local_index(symbol)
        if not is_absent_index(idx):
            return idx

        idx = scope.add_local(symbol)
        assert not is_absent_index(idx)
        return idx

    def get_variable_index(self, name):
        """
            return var_index, is_local_variable
        """
        scope_id = 0
        for scope in reversed(self.scopes):
            idx = scope.get_local_index(name)
            if not is_absent_index(idx):
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
        # print 'closing scope, returning to %d' % (self.depth, )

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
        if is_list_node(ast):
            self._compile_nodes(code, ast)
        else:
            self._compile_node(code, ast)

    def _compile_nodes(self, bytecode, ast):
        nodes = ast.items

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

        if TT_INT == t:
            self._compile_INT(code, node)
        elif TT_FLOAT == t:
            self._compile_FLOAT(code, node)
        elif TT_STR == t:
            self._compile_STR(code, node)
        elif TT_CHAR == t:
            self._compile_CHAR(code, node)
        elif TT_NAME == t:
            self._compile_NAME(code, node)
        elif TT_BREAK == t:
            self._compile_BREAK(code, node)
        elif TT_CONTINUE == t:
            self._compile_CONTINUE(code, node)
        elif TT_FOR == t:
            self._compile_FOR(code, node)
        elif TT_WHILE == t:
            self._compile_WHILE(code, node)
        elif TT_IF == t:
            self._compile_IF(code, node)
        elif TT_WHEN == t:
            self._compile_WHEN(code, node)
        elif TT_FN == t:
            self._compile_FN(code, node)
        elif TT_AND == t:
            self._compile_AND(code, node)
        elif TT_OR == t:
            self._compile_OR(code, node)
        elif TT_NOT == t:
            self._compile_NOT(code, node)
        elif TT_TRUE == t:
            self._compile_TRUE(code, node)
        elif TT_FALSE == t:
            self._compile_FALSE(code, node)
        elif TT_NIL == t:
            self._compile_NIL(code, node)
        elif TT_UNDEFINED == t:
            self._compile_UNDEFINED(code, node)
        elif TT_IN == t:
            self._compile_IN(code, node)
        elif TT_IS == t:
            self._compile_IS(code, node)
        elif TT_OBJECT == t:
            self._compile_OBJECT(code, node)
        elif TT_ISNOT == t:
            self._compile_ISNOT(code, node)
        elif TT_OUTER == t:
            self._compile_OUTER(code, node)
        elif TT_IMPORT == t:
            self._compile_IMPORT(code, node)
        elif TT_TRAIT == t:
            self._compile_TRAIT(code, node)
        elif TT_GENERIC == t:
            self._compile_GENERIC(code, node)
        elif TT_REIFY == t:
            self._compile_REIFY(code, node)
        elif TT_RETURN == t:
            self._compile_RETURN(code, node)
        elif TT_ADD_ASSIGN == t:
            self._compile_ADD_ASSIGN(code, node)
        elif TT_SUB_ASSIGN == t:
            self._compile_SUB_ASSIGN(code, node)
        elif TT_MUL_ASSIGN == t:
            self._compile_MUL_ASSIGN(code, node)
        elif TT_DIV_ASSIGN == t:
            self._compile_DIV_ASSIGN(code, node)
        elif TT_MOD_ASSIGN == t:
            self._compile_MOD_ASSIGN(code, node)
        elif TT_BITAND_ASSIGN == t:
            self._compile_BITAND_ASSIGN(code, node)
        elif TT_BITXOR_ASSIGN == t:
            self._compile_BITXOR_ASSIGN(code, node)
        elif TT_BITOR_ASSIGN == t:
            self._compile_BITOR_ASSIGN(code, node)
        elif TT_RSHIFT == t:
            self._compile_RSHIFT(code, node)
        elif TT_URSHIFT == t:
            self._compile_URSHIFT(code, node)
        elif TT_LSHIFT == t:
            self._compile_LSHIFT(code, node)
        elif TT_EQ == t:
            self._compile_EQ(code, node)
        elif TT_LE == t:
            self._compile_LE(code, node)
        elif TT_GE == t:
            self._compile_GE(code, node)
        elif TT_NE == t:
            self._compile_NE(code, node)
        elif TT_LCURLY == t:
            self._compile_LCURLY(code, node)
        elif TT_ASSIGN == t:
            self._compile_ASSIGN(code, node)
        elif TT_LPAREN == t:
            self._compile_LPAREN(code, node)
        elif TT_LSQUARE == t:
            self._compile_LSQUARE(code, node)
        elif TT_DOT == t:
            self._compile_DOT(code, node)
        elif TT_BITAND == t:
            self._compile_BITAND(code, node)
        elif TT_BITNOT == t:
            self._compile_BITNOT(code, node)
        elif TT_BITOR == t:
            self._compile_BITOR(code, node)
        elif TT_BITXOR == t:
            self._compile_BITXOR(code, node)
        elif TT_SUB == t:
            self._compile_SUB(code, node)
        elif TT_ADD == t:
            self._compile_ADD(code, node)
        elif TT_MUL == t:
            self._compile_MUL(code, node)
        elif TT_DIV == t:
            self._compile_DIV(code, node)
        elif TT_MOD == t:
            self._compile_MOD(code, node)
        elif TT_LT == t:
            self._compile_LT(code, node)
        elif TT_GT == t:
            self._compile_GT(code, node)

    def _compile_FLOAT(self, bytecode, node):
        value = float(node.value)
        idx = self.declare_literal(obs.newfloat(value))
        bytecode.emit_1(LITERAL, idx)

    def _compile_INT(self, bytecode, node):
        value = int(node.value)
        idx = self.declare_literal(obs.newint(value))
        bytecode.emit_1(LITERAL, idx)

    def _compile_TRUE(self, bytecode, node):
        bytecode.emit_0(TRUE)

    def _compile_FALSE(self, bytecode, node):
        bytecode.emit_0(FALSE)

    def _compile_NIL(self, bytecode, node):
        bytecode.emit_0(NULL)

    def _compile_UNDEFINED(self, bytecode, node):
        bytecode.emit_0(UNDEFINED)

    def _emit_string(self, bytecode, string):
        idx = self.declare_literal(string)
        bytecode.emit_1(LITERAL, idx)

    def _compile_STR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        self._emit_string(bytecode, obs.newstring(strval))

    def _compile_CHAR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        self._emit_string(bytecode, obs.newstring(strval))

    def _compile_OUTER(self, bytecode, node):
        name = obs.newstring_from_str(node.first().value)
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
        name = obs.newstring_from_str(member.second().value)

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

        name = obs.newstring_from_str(left.value)
        # self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        self._emit_store(bytecode, name)

    def _compile_modify_assignment_dot_primitive(self, bytecode, node, operation):
        member = node.first()
        name = obs.newstring_from_str(member.second().value)

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

        name = obs.newstring_from_str(left.value)
        if not self.is_modifiable_binding(name):
            compile_error_1(node, "Unreachable variable", name)

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

    def _compile_name_lookup(self, code, node):
        name = obs.newstring_from_str(node.value)

        index, is_local = self.get_variable_index(name)
        name_index = self.declare_literal(name)
        if is_local:
            code.emit_2(LOCAL, index, name_index)
        else:
            code.emit_2(OUTER, index, name_index)

    def _compile_NAME(self, code, node):
        self._compile_name_lookup(code, node)

    def _compile_RETURN(self, code, node):
        expr = node.first()
        if is_empty_node(expr):
            code.emit_0(UNDEFINED)
        else:
            self._compile(code, expr)

        code.emit_0(RETURN)

    def _compile_RAISE(self, code, node):
        expr = node.first()
        if is_empty_node(expr):
            code.emit_0(UNDEFINED)
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
                self._emit_string(code, obs.newstring_from_str(key.value))
            else:
                self._compile(code, key)

        code.emit_2(OBJECT, len(items), len(traits))

    def _compile_LCURLY(self, code, node):
        items = node.first()
        self._compile_object(code, items, list_node([]))

    def _compile_OBJECT_expression(self, code, node):
        traits = node.first()
        items = node.second()
        self._compile_object(code, items, traits)

    def _compile_OBJECT(self, code, node):
        """
        compiles object statements
        """
        if node.arity == 2:
            return self._compile_OBJECT_expression(code, node)

        name = node.first()
        traits = node.second()
        items = node.third()
        self._compile_object(code, items, traits)

        name = obs.newstring_from_str(name.value)
        index = self.declare_local(name)
        name_index = self.declare_literal(name)
        # self._compile(bytecode, node.first())
        code.emit_2(STORE_LOCAL, index, name_index)

    def _compile_TUPLE(self, code, node):
        items = node.first()
        for c in items:
            self._compile(code, c)

        code.emit_1(TUPLE, len(items))

    def _compile_LSQUARE(self, code, node):
        # lookup like a[0]
        if node.arity == 2:
            return self._compile_LSQUARE_lookup(code, node)

        items = node.first()
        for c in items:
            self._compile(code, c)

        code.emit_1(VECTOR, len(items))

    def _compile_BREAK(self, code, node):
        code.emit_0(UNDEFINED)
        if not code.emit_break():
            compile_error(node, "break outside loop")

    def _compile_CONTINUE(self, code, node):
        code.emit_0(UNDEFINED)
        if not code.emit_continue():
            compile_error(node, "continue outside loop")

    def _compile_fn_args_and_body(self, code, funcname, params, outers, body):
        self.enter_scope()

        if is_iterable_node(params):
            length = len(params)
            last_index = length - 1
            args = []
            for i in range(0, last_index):
                param = params[i]
                args.append(obs.newstring_from_str(param.value))

            lastparam = params[last_index]

            if lastparam.type == TT_ELLIPSIS:
                args.append(obs.newstring_from_str(lastparam.first().value))
                varargs = True
            else:
                args.append(obs.newstring_from_str(lastparam.value))
                varargs = False
        else:
            args = None
            varargs = False

        self.declare_arguments(args, varargs)

        if is_iterable_node(outers):
            for outer in outers:
                self.declare_outer(obs.newstring_from_str(outer.value))

        if not funcname.isempty():
            self.declare_function_name(funcname)

        funccode = CodeSource()
        self._compile(funccode, body)
        current_scope = self.current_scope()
        scope = current_scope.finalize()
        self.exit_scope()
        # print "LOCALS:", str(scope.variables.keys())
        # print "REFS:", str(scope.references)
        compiled_code = funccode.finalize_compilation(scope)
        # print [str(c) for c in compiled_code.opcodes]
        # print "-------------------------"

        source = obs.newfuncsource(funcname, compiled_code)
        source_index = self.declare_literal(source)
        code.emit_1(FUNCTION, source_index)

    def _compile_FN_expression(self, code, node):
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
            return self._compile_FN_expression(code, node)

        name = node.first()
        funcname = obs.newstring_from_str(name.value)

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

    def _compile_WHEN(self, code, node):
        condition = node.first()
        truebranch = node.second()
        falsebranch = node.third()
        endif = code.prealocate_label()
        self._compile_branch(code, condition, truebranch, endif)
        self._compile(code, falsebranch)
        code.emit_1(LABEL, endif)

    def _compile_IF(self, code, node):
        branches = node.first()

        endif = code.prealocate_label()

        for i in range(len(branches) - 1):
            branch = branches[i]
            self._compile_branch(code, branch[0], branch[1], endif)

        elsebranch = branches[-1]
        if is_empty_node(elsebranch):
            code.emit_0(UNDEFINED)
        else:
            self._compile(code, elsebranch[1])

        code.emit_1(LABEL, endif)

    def _dot_to_string(self, node):
        if node.type == TT_DOT:
            return self._dot_to_string(node.first()) + '.' + node.second().value
        else:
            return node.value

    def _compile_IMPORT_single(self, code, node):
        exp = node.first()
        if exp.type == TT_AS:
            import_name = exp.second().value
            module_path = self._dot_to_string(exp.first())
        elif exp.type == TT_DOT:
            import_name = exp.second().value
            module_path = self._dot_to_string(exp)
        else:
            assert exp.type == TT_NAME
            import_name = node.value
            module_path = import_name

        module_path = obs.newstring_from_str(module_path)
        import_name = obs.newstring_from_str(import_name)

        module_path_literal = self.declare_literal(module_path)
        code.emit_1(IMPORT, module_path_literal)

        import_name_literal = self.declare_literal(import_name)
        import_name_index = self.declare_local(import_name)
        code.emit_2(STORE_LOCAL, import_name_index, import_name_literal)

    def _compile_IMPORT_destructuring(self, code, node):
        items = node.first()
        module = node.second()
        module_path = self._dot_to_string(module)
        module_path = obs.newstring_from_str(module_path)
        module_path_literal = self.declare_literal(module_path)
        code.emit_1(IMPORT, module_path_literal)
        for item in items:
            if item.type == TT_AS:
                var_name = item.second().value
                module_var = item.first().value
            else:
                assert item.type == TT_NAME
                var_name = item.value
                module_var = var_name

            var_name = obs.newstring_from_str(var_name)
            module_var = obs.newstring_from_str(module_var)

            module_var_literal = self.declare_literal(module_var)
            code.emit_1(IMPORT_MEMBER, module_var_literal)

            var_name_literal = self.declare_literal(var_name)
            var_name_index = self.declare_local(var_name)
            code.emit_2(STORE_LOCAL, var_name_index, var_name_literal)
            code.emit_0(POP)

    def _compile_IMPORT(self, code, node):
        if node.arity == 1:
            self._compile_IMPORT_single(code, node)
        elif node.arity == 2:
            self._compile_IMPORT_destructuring(code, node)
        else:
            compile_error(node, "Invalid import statement")

    def _compile_GENERIC(self, code, node):
        name = node.first()
        name = obs.newstring_from_str(name.value)
        index = self.declare_local(name)
        name_index = self.declare_literal(name)
        code.emit_1(GENERIC, name_index)
        code.emit_2(STORE_LOCAL, index, name_index)
        if node.arity == 2:
            self._compile_REIFY(code, node)

    def _compile_TRAIT(self, code, node):
        name = node.first()
        name = obs.newstring_from_str(name.value)
        index = self.declare_local(name)
        name_index = self.declare_literal(name)
        code.emit_1(TRAIT, name_index)
        code.emit_2(STORE_LOCAL, index, name_index)

    def _compile_REIFY(self, code, node):
        name = node.first()
        self._compile_name_lookup(code, name)
        methods = node.second()

        for method in methods:
            method_args = method[0]
            method_body = method[1]
            args = []
            signature = []
            for arg in method_args:
                if arg.type == TT_OF:
                    args.append(arg.first())
                    signature.append(arg.second())
                else:
                    args.append(arg)
                    signature.append(None)

            for trait in signature:
                if trait is None:
                    code.emit_0(UNDEFINED)
                else:
                    self._compile(code, trait)

            code.emit_1(TUPLE, len(signature))

            method_name = obs.newstring(u"")
            self._compile_fn_args_and_body(code, method_name, list_node(args), empty_node(), method_body)
            code.emit_1(TUPLE, 2)

        code.emit_1(REIFY, len(methods))

    def _compile_FOR(self, bytecode, node):
        vars = node.first()
        name = obs.newstring_from_str(vars[0].value)

        source = node.second()
        body = node.third()
        self._compile(bytecode, source)
        bytecode.emit_0(ITERATOR)
        # load the "last" iterations result
        bytecode.emit_0(UNDEFINED)
        precond = bytecode.emit_startloop_label()
        bytecode.continue_at_label(precond)
        finish = bytecode.prealocate_endloop_label(False)
        # update = bytecode.prealocate_updateloop_label()

        bytecode.emit_1(JUMP_IF_ITERATOR_EMPTY, finish)

        # put next iterator value on stack
        bytecode.emit_0(NEXT)

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
        bytecode.emit_0(UNDEFINED)
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
        name = obs.newstring_from_str(node.second().value)
        self._emit_string(code, name)
        obj = node.first()
        self._compile(code, obj)
        code.emit_0(MEMBER_DOT)
        # TODO LITERAL HERE
        # self.declare_symbol(name)

    def _compile_LSQUARE_lookup(self, code, node):
        expr = node.second()
        self._compile(code, expr)
        obj = node.first()
        self._compile(code, obj)
        code.emit_0(MEMBER)

    def _compile_args_list(self, code, args):
        normal_args_count = 0
        first_args_inserted = False
        if len(args) == 0:
            code.emit_1(VECTOR, 0)
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
                        code.emit_1(VECTOR, normal_args_count)
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
                code.emit_1(VECTOR, normal_args_count)

    def _compile_LPAREN_member(self, bytecode, node):
        obj = node.first()
        method = node.second()
        name = obs.newstring_from_str(method.value)
        args = node.third()
        # print "_compile_LPAREN_MEMBER", obj, method, args

        self._compile_args_list(bytecode, args)

        self._compile(bytecode, obj)
        self._emit_string(bytecode, name)
        # TODO LITERAL HERE
        # self.declare_symbol(name)

        bytecode.emit_0(CALL_METHOD)

    def _compile_LPAREN(self, bytecode, node):
        if node.arity == 1:
            return self._compile_TUPLE(bytecode, node)
        elif node.arity == 3:
            return self._compile_LPAREN_member(bytecode, node)

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
# fn _(x, y) {
#     print("x - y", x - y)
# } (30, 20)
# """)
"""
    reify fire {
        (self of Soldier, other of Civilian) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
        (self of Soldier, other1, other2) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
        (self, other1, other2, other3 of Enemy) {
            attack(self, other)
            name = self.name
            surname = "Surname" + name + other.name
        }
    }
"""
