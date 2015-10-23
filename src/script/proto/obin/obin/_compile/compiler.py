__author__ = 'gloryofrobots'
from token_type import *
from tokens import TT_TO_STR
from _parser import *

from obin.objects.symbol_map import SymbolMap


class Position(object):
    def __init__(self, lineno=-1, start=-1):
        self.lineno = lineno
        self.start = start

    def __repr__(self):
        return "l:%d %d" % (self.lineno, self.start)

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
        s = unicode(symbol)
        #assert isinstance(s, unicode)
        idx = self.scopes[-1].add_symbol(s)
        #print 'symbol "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_variable(self, symbol):
        s = unicode(symbol)
        #assert isinstance(s, unicode)
        idx = self.scopes[-1].add_variable(s)
        #print 'var declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_function(self, symbol, funcobj):
        s = unicode(symbol)
        #assert isinstance(s, unicode)
        self.funclists[-1][s] = funcobj
        idx = self.scopes[-1].add_function(s)
        #print 'func declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
        return idx

    def declare_parameter(self, symbol):
        idx = self.scopes[-1].add_parameter(symbol)
        #print 'parameter declaration "%s"@%d in scope %d' % (symbol, idx, self.depth,)
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

    def get_pos(self, node):
        return Position(
            node.line,
            node.position
        )

    def compile(self, ast):
        from bytecode import ByteCode
        code = ByteCode()
        self.enter_scope()
        self._compile(code, ast)
        scope = self.current_scope()
        final_scope = scope.finalize()
        code.set_symbols(final_scope)
        return code

    def _compile(self, code, ast):
        if isinstance(ast, list):
            return self._compile_nodes(code, ast)
        else:
            return self._compile_node(code, ast)

    def _compile_nodes(self, bytecode, nodes):
        if len(nodes) > 1:
            for node in nodes[:-1]:
                self._compile_node(bytecode, node)
                bytecode.emit('POP')

        if len(nodes) > 0:
            node = nodes[-1]
            self._compile_node(bytecode, node)
        else:
            bytecode.emit('LOAD_UNDEFINED')

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

    def _compile_STRING(self, bytecode, node):
        from obin.compile.operations import string_unquote
        from obin.runistr import unicode_unescape, decode_str_utf8

        s = str(node.value)
        strval = decode_str_utf8(s)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        bytecode.emit('LOAD_STRINGCONSTANT', strval)

    def _compile_CHAR(self, bytecode, node):
        from obin.compile.operations import string_unquote
        from obin.runistr import unicode_unescape, decode_str_utf8

        s = str(node.value)
        strval = decode_str_utf8(s)
        strval = string_unquote(strval)
        strval = unicode_unescape(strval)
        bytecode.emit('LOAD_STRINGCONSTANT', strval)

    def compile_binary(self, code, node, name):
        self._compile(code, node.first())
        self._compile(code, node.second())
        code.emit(name)

    def _compile_BITAND(self, code, node):
        self.compile_binary(code, node, "BITAND")

    def _compile_BITOR(self, code, node):
        self.compile_binary(code, node, "BITOR")

    def _compile_BITXOR(self, code, node):
        self.compile_binary(code, node, "BITXOR")

    def _compile_BITNOT(self, code, node):
        self.compile_binary(code, node, "BITNOT")

    def _compile_ADD(self, code, node):
        self.compile_binary(code, node, "ADD")

    def _compile_MUL(self, code, node):
        self.compile_binary(code, node, "MUL")

    def _compile_MOD(self, code, node):
        self.compile_binary(code, node, "MOD")

    def _compile_DIV(self, code, node):
        self.compile_binary(code, node, "DIV")

    def _compile_SUB(self, code, node):
        self.compile_binary(code, node, "SUB")

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

    def _compile_ASSIGN(self, bytecode, node):
        left = node.first()
        index = self.declare_variable(left.value)
        # self._compile(bytecode, left)
        self._compile(bytecode, node.second())
        bytecode.emit('STORE', index, unicode(left.value))


def testprogram():
    data = ""
    with open("program2.obn") as f:
        data = f.read()

    return data

def compile(txt):
    ast = parse_string(txt)
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

compile_and_print("""
x = 2 + 3
y = 2 + 4 * 6
""")

test(
"""
x = 2 + 3;
y = 2 + 4 * 6 / 12
""",
"""
var x = 2 + 3;
var y = 2 + 4 * 6 / 12;
"""
)