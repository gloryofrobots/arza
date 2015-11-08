__author__ = 'gloryofrobots'
from token_type import *
from tokens import TT_TO_STR
from _parser import *

from obin.objects.symbol_map import SymbolMap
from obin.objects.object_space import newstring, isstring

def error(node, message, args):
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

        new_scope = SymbolMap()
        self.scopes.append(new_scope)
        #print 'starting new scope %d' % (self.depth, )

    def declare_symbol(self, symbol):
        assert symbol
        s = newstring(symbol)
        idx = self.scopes[-1].add_symbol(s)
        # print "SYMBOL", symbol, len(symbol), idx
        return idx

    def has_variable(self, symbol):
        return self.scopes[-1].has_variable(symbol)

    def declare_variable(self, symbol):
        assert symbol
        # print "VAR", symbol
        s = newstring(symbol)
        idx = self.scopes[-1].add_variable(s)
        #print 'var declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_function(self, symbol, funcobj):
        assert symbol
        s = newstring(symbol)
        # self.funclists[-1][s] = funcobj
        idx = self.scopes[-1].add_function(s)
        #print 'func declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_parameter(self, symbol):
        assert symbol
        idx = self.scopes[-1].add_parameter(symbol)
        #print 'parameter declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_rest(self, symbol):
        assert symbol
        idx = self.scopes[-1].add_rest(newstring(symbol))
        #print 'rest declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def exit_scope(self):
        self.depth = self.depth - 1
        self.scopes.pop()
        #print 'closing scope, returning to %d' % (self.depth, )

    def current_scope_variables(self):
        return self.current_scope().variables

    def current_scope_parameters(self):
        return self.current_scope().parameters

    def current_scope(self):
        try:
            return self.scopes[-1]
        except IndexError:
            return None

    def set_sourcename(self, sourcename):
        self.stsourcename = sourcename  # XXX I should call this

    def compile(self, ast):
        from bytecode import ByteCode
        code = ByteCode()
        self.enter_scope()
        self._compile(code, ast)
        code.emit('LOAD_UNDEFINED')
        scope = self.current_scope()
        final_scope = scope.finalize()
        code.set_symbols(final_scope)
        return code

    def _compile(self, code, ast):
        if isinstance(ast, list):
            self._compile_nodes(code, ast)
        else:
            self._compile_node(code, ast)

    def _compile_nodes(self, bytecode, nodes):
        from obin.runtime.opcodes import POP
        if len(nodes) > 1:

            for node in nodes[:-1]:
                self._compile_node(bytecode, node)
                # last = bytecode.opcodes[-1]
                # if not isinstance(last, POP):
                bytecode.emit('POP')

        if len(nodes) > 0:
            node = nodes[-1]
            self._compile_node(bytecode, node)


    def _compile_node(self, code, node):
        t = node.type
        t_str = TT_TO_STR(t).replace("TT_", "")
        compiler = getattr(self, "_compile_" + t_str)
        return compiler(code, node)

    def _compile_FLOAT(self, bytecode, node):
        value = float(node.value)
        bytecode.emit('LOAD_FLOATCONSTANT', value)

    def _compile_INT(self, bytecode, node):
        value = int(node.value)
        bytecode.emit('LOAD_INTCONSTANT', value)

    def _compile_TRUE(self, bytecode, node):
        bytecode.emit('LOAD_BOOLCONSTANT', True)

    def _compile_FALSE(self, bytecode, node):
        bytecode.emit('LOAD_BOOLCONSTANT', True)

    def _compile_NIL(self, bytecode, node):
        bytecode.emit('LOAD_NULL')

    def _compile_UNDEFINED(self, bytecode, node):
        bytecode.emit('LOAD_UNDEFINED')

    def _compile_STR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        bytecode.emit('LOAD_STRINGCONSTANT', newstring(strval))

    def _compile_CHAR(self, bytecode, node):
        from obin.runistr import unicode_unescape, decode_str_utf8

        strval  = str(node.value)
        strval = decode_str_utf8(strval)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        bytecode.emit('LOAD_STRINGCONSTANT', newstring(strval))

    def compile_binary(self, code, node, name):
        self._compile(code, node.first())
        self._compile(code, node.second())
        code.emit(name)

    def compile_unary(self, code, node, name):
        self._compile(code, node.first())
        code.emit(name)

    def _compile_BITAND(self, code, node):
        self.compile_binary(code, node, "BITAND")

    def _compile_BITOR(self, code, node):
        self.compile_binary(code, node, "BITOR")

    def _compile_BITXOR(self, code, node):
        self.compile_binary(code, node, "BITXOR")

    def _compile_ADD(self, code, node):
        if node.arity == 2:
            self.compile_binary(code, node, "ADD")
        elif node.arity == 1:
            self.compile_unary(code, node, "UPLUS")
        else:
            assert 0

    def _compile_MUL(self, code, node):
        self.compile_binary(code, node, "MUL")

    def _compile_MOD(self, code, node):
        self.compile_binary(code, node, "MOD")

    def _compile_DIV(self, code, node):
        self.compile_binary(code, node, "DIV")

    def _compile_SUB(self, code, node):
        if node.arity == 2:
            self.compile_binary(code, node, "SUB")
        elif node.arity == 1:
            self.compile_unary(code, node, "UMINUS")
        else:
            assert 0

    def _compile_BITNOT(self, code, node):
        self.compile_unary(code, node, "BITNOT")

    def _compile_NOT(self, code, node):
        self.compile_unary(code, node, "NOT")

    def _compile_GE(self, code, node):
        self.compile_binary(code, node, "GE")

    def _compile_GT(self, code, node):
        self.compile_binary(code, node, "GT")

    def _compile_LE(self, code, node):
        self.compile_binary(code, node, "LE")

    def _compile_LT(self, code, node):
        self.compile_binary(code, node, "LT")

    def _compile_IS(self, code, node):
        self.compile_binary(code, node, "IS")

    def _compile_ISNOT(self, code, node):
        self.compile_binary(code, node, "ISNOT")

    def _compile_IN(self, code, node):
        self.compile_binary(code, node, "IN")

    def _compile_EQ(self, code, node):
        self.compile_binary(code, node, "EQ")

    def _compile_NE(self, code, node):
        self.compile_binary(code, node, "NE")

    def _compile_LSHIFT(self, code, node):
        self.compile_binary(code, node, "LSH")

    def _compile_RSHIFT(self, code, node):
        self.compile_binary(code, node, "RSH")

    def _compile_URSHIFT(self, code, node):
        self.compile_binary(code, node, "URSH")

    def _compile_AND(self, bytecode, node):
        self._compile(bytecode, node.first())
        one = bytecode.prealocate_label()
        bytecode.emit('JUMP_IF_FALSE_NOPOP', one)
        self._compile(bytecode, node.second())
        bytecode.emit('LABEL', one)

    def _compile_OR(self, bytecode, node):
        self._compile(bytecode, node.first())
        one = bytecode.prealocate_label()
        bytecode.emit('JUMP_IF_TRUE_NOPOP', one)
        self._compile(bytecode, node.second())
        bytecode.emit('LABEL', one)

    def _compile_variable_declaration(self, bytecode, node, value):
        index = self.declare_variable(value)
        self._compile(bytecode, node.second())
        bytecode.emit('STORE', index, value)

    def _compile_ASSIGN_DOT(self, bytecode, node):
        member = node.first()
        name = member.second()

        obj = member.first()
        self._compile(bytecode, node.second())
        bytecode.emit('LOAD_STRINGCONSTANT', newstring(name.value))
        # self._compile(bytecode, name)
        self._compile(bytecode, obj)
        bytecode.emit('STORE_MEMBER')

    def _compile_ASSIGN(self, bytecode, node):
        left = node.first()
        if left.type == TT_DOT:
            return self._compile_ASSIGN_DOT(bytecode, node)

        index = self.declare_variable(left.value)
        # self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        bytecode.emit('STORE', index, newstring(left.value))

    def _compile_modify_assignment(self, bytecode, node, operation):
        left = node.first()
        index = self.declare_variable(left.value)
        # self._compile(bytecode, left)

        self._compile(bytecode, node.first())
        self._compile(bytecode, node.second())
        bytecode.emit(operation)
        bytecode.emit('STORE', index, newstring(left.value))

    def _compile_ADD_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "ADD")

    def _compile_SUB_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "SUB")

    def _compile_MUL_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "MUL")

    def _compile_DIV_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "DIV")

    def _compile_MOD_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "MOD")

    def _compile_BITOR_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "BITOR")

    def _compile_BITAND_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "BITAND")

    def _compile_BITXOR_ASSIGN(self, code, node):
        self._compile_modify_assignment(code, node, "BITXOR")

    def _compile_NAME(self, code, node):
        name = newstring(node.value)
        index = self.declare_symbol(node.value)
        code.emit('LOAD_VARIABLE', index, name)

    def is_empty(self, l):
        return isinstance(l, list) and len(l) == 0

    def _compile_THIS(self, code, node):
        code.emit('LOAD_THIS')

    def _compile_RETURN(self, code, node):
        expr = node.first()
        if self.is_empty(expr):
            code.emit('LOAD_UNDEFINED')
        else:
            self._compile(code, expr)

        code.emit('RETURN')

    def _compile_RAISE(self, code, node):
        expr = node.first()
        if self.is_empty(expr):
            code.emit('LOAD_UNDEFINED')
        else:
            self._compile(code, expr)

        code.emit('THROW')

    def _compile_LCURLY(self, code, node):
        items = node.first()
        for c in items:
            key = c[0]
            value = c[1]

            self._compile(code, value)
            if key.type == TT_NAME:
                # in case of names in object literal we must convert them to strings
                code.emit('LOAD_STRINGCONSTANT', newstring(key.value))
            else:
                self._compile(code, key)

        code.emit("LOAD_OBJECT", len(items))

    def _compile_LSQUARE(self, code, node):
        # lookup like a[0]
        if node.arity == 2:
            return self._compile_LSQUARE_LOOKUP(code, node)

        items = node.first()
        for c in items:
            self._compile(code, c)

        code.emit("LOAD_VECTOR", len(items))

    def _compile_BREAK(self, code, node):
        code.emit('LOAD_UNDEFINED')
        code.emit_break()

    def _compile_CONTINUE(self, code, node):
        code.emit('LOAD_UNDEFINED')
        code.emit_continue()

    def _compile_FN(self, code, node):
        from bytecode import ByteCode

        name = node.first()
        params = node.second()
        body = node.third()

        if self.is_empty(name):
            funcname = u''
            index = None
        else:
            funcname = unicode(name.value)
            index = self.declare_symbol(funcname)

        self.enter_scope()
        if len(funcname):
            self.declare_symbol(funcname)

        if params:
            for param in params[:-1]:
                self.declare_parameter(newstring(param.value))

            lastparam = params[-1]
            if lastparam.type == TT_ELLIPSIS:
                self.declare_rest(newstring(lastparam.first().value))
            else:
                self.declare_parameter(newstring(lastparam.value))

        funccode = ByteCode()

        self._compile(funccode, body)
        funccode.emit('LOAD_UNDEFINED')
        current_scope = self.current_scope()
        scope = current_scope.finalize()
        self.exit_scope()
        print str(scope.symbols)
        funccode.set_symbols(scope)
        print [str(c) for c in funccode.opcodes]
        print "-------------------------"

        code.emit('LOAD_FUNCTION', newstring(funcname), funccode)

        if index is not None and len(funcname):
            # self.declare_function(funcname, func)
            code.emit('STORE', index, newstring(funcname))

        # code.emit('POP')

    def _compile_branch(self, bytecode, condition, body, endif):
        self._compile(bytecode, condition)
        end_body = bytecode.prealocate_label()
        bytecode.emit('JUMP_IF_FALSE', end_body)
        self._compile(bytecode, body)
        bytecode.emit('JUMP', endif)
        bytecode.emit('LABEL', end_body)

    def _compile_IF_TERNARY(self, code, node):
        condition = node.first()
        truebranch = node.second()
        falsebranch = node.third()
        endif = code.prealocate_label()
        self._compile_branch(code, condition, truebranch, endif)
        self._compile(code, falsebranch)
        code.emit('LABEL', endif)

    def _compile_IF(self, code, node):
        if node.arity == 3:
            return self._compile_IF_TERNARY(code, node)
        branches = node.first()

        endif = code.prealocate_label()

        for i in range(len(branches) - 1):
            branch = branches[i]
            self._compile_branch(code, branch[0], branch[1], endif)

        elsebranch = branches[-1]
        if self.is_empty(elsebranch):
            code.emit('LOAD_UNDEFINED')
        else:
            self._compile(code, elsebranch[1])

        code.emit('LABEL', endif)

    def _compile_WHILE(self, bytecode, node):
        condition = node.first()
        body = node.second()
        bytecode.emit('LOAD_UNDEFINED')
        startlabel = bytecode.emit_startloop_label()
        bytecode.continue_at_label(startlabel)
        self._compile(bytecode, condition)
        endlabel = bytecode.prealocate_endloop_label()
        bytecode.emit('JUMP_IF_FALSE', endlabel)
        bytecode.emit('POP')
        self._compile(bytecode, body)
        bytecode.emit('JUMP', startlabel)
        bytecode.emit_endloop_label(endlabel)
        bytecode.done_continue()

    def _compile_DOT(self, code, node):
        name = node.second().value
        code.emit("LOAD_STRINGCONSTANT", newstring(name))
        obj = node.first()
        self._compile(code, obj)
        code.emit('LOAD_MEMBER_DOT')
        self.declare_symbol(name)

    def _compile_ELLIPSIS(self, code, node):
        pass

    def _compile_LSQUARE_LOOKUP(self, code, node):
        expr = node.second()
        self._compile(code, expr)
        obj = node.first()
        self._compile(code, obj)
        code.emit('LOAD_MEMBER')

    def _compile_args_list(self, code, args):
        # create tuples and unpack instruction for function call
        length = 0
        normal_args_count = 0
        for arg in args:
            if arg.type == TT_ELLIPSIS:
                if normal_args_count:
                    code.emit("LOAD_LIST", normal_args_count)
                    normal_args_count = 0
                    length += 1
                self._compile(code, arg.first())
                # code.emit("UNPACK")
                length += 1
            else:
                self._compile(code, arg)
                normal_args_count += 1

        if normal_args_count:
            code.emit("LOAD_LIST", normal_args_count)
            length += 1

        return length

    def _compile_LPAREN_MEMBER(self, bytecode, node):
        obj = node.first()
        method = node.second()
        name = method.value
        args = node.third()
        # print "_compile_LPAREN_MEMBER", obj, method, args

        length = self._compile_args_list(bytecode, args)

        self._compile(bytecode, obj)
        bytecode.emit('LOAD_STRINGCONSTANT', newstring(name))
        self.declare_symbol(name)

        bytecode.emit("CALL_METHOD", length)

    def _compile_LPAREN(self, bytecode, node):
        if node.arity == 3:
            return self._compile_LPAREN_MEMBER(bytecode, node)

        func = node.first()
        args = node.second()

        # print "_compile_LPAREN", func, args

        length = self._compile_args_list(bytecode, args)

        self._compile(bytecode, func)

        bytecode.emit("CALL", length)

def testprogram():
    data = ""
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

def compile_old(txt):
    from obin.compile.astbuilder import parse_to_ast
    from obin.runistr import decode_str_utf8
    from obin.compile.code import ast_to_bytecode
    ast = parse_to_ast(decode_str_utf8(txt))
    symbol_map = ast.symbol_map
    code = ast_to_bytecode(ast, symbol_map)
    return code


def _check(val1, val2):
    print val1
    print val2
    if val1 != val2:
        print val1
        print val2
        raise RuntimeError("Not equal")

def check_codes(first, second):
    print "**************************************************************"
    print str(first._symbols.symbols)
    print str(second._symbols.symbols)
    self_str = str([str(c) for c in first.opcodes])
    other_str = str([str(c) for c in second.opcodes])
    _check(self_str, other_str)
    _check(first.label_count, second.label_count)
    _check(first.has_labels, second.has_labels)
    _check(first.startlooplabel, second.startlooplabel)
    _check(first.endlooplabel, second.endlooplabel)
    _check(first.pop_after_break, second.pop_after_break)
    _check(first.updatelooplabel, second.updatelooplabel)
    _check(first._function_name_, second._function_name_)
    _check(str(first._symbols.symbols), str(second._symbols.symbols))
    _check(str(first._symbols.functions), str(second._symbols.functions))
    _check(str(first._symbols.functions), str(second._symbols.functions))
    _check(first.parameters, second.parameters)

def test(txt, txt_old):
    code = compile(txt)
    code_old = compile_old(txt_old)
    check_codes(code, code_old)

# compile_and_print("""
# fn f(x, y, z){ return x + y + z; }
# fn f2() {}
# """)
# compile_old("var x = (y > 0) ? 1: 2;")
#
# test(
# """
# F = fn{
# }
# F.action = fn {
#     print("OLOLO")
# }
# F.action()
# """,
# """
# F = function(){
# };
# F.action = function() {
#     print("OLOLO");
# };
# F.action();
# """
# )

