from __future__ import division

import py
from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.parsing import Rule, ParseError
from rpython.rlib.parsing.tree import RPythonVisitor
from pypy import conftest

from js.astbuilder import FakeParseError
from js.astbuilder import ASTBuilder
from js.jscode import JsCode


xfail = py.test.mark.xfail

GFILE = py.path.local(__file__).dirpath().join('../js/jsgrammar.txt')
try:
    t = GFILE.read(mode='U')
    regexs, rules, ToAST = parse_ebnf(t)
except ParseError, e:
    print e.nice_error_message(filename=str(GFILE), source=t)
    raise

parse_function = make_parse_function(regexs, rules, eof=True)


def setstartrule(rules, start):
    "takes the rule start and put it on the beginning of the rules"
    newrules = [Rule("hacked_first_symbol", [[start, "EOF"]])] + rules
    return newrules


def get_defaultparse():
    return parse_function


def parse_func(start=None):
    if start is not None:
        parse_function = make_parse_function(regexs, setstartrule(rules, start), eof=True)
    else:
        parse_function = get_defaultparse()

    def methodparse(self, text):
        tree = parse_function(text)
        if start is not None:
            assert tree.symbol == "hacked_first_symbol"
            tree = tree.children[0]
        tree = tree.visit(ToAST())[0]
        if conftest.option and conftest.option.view:
            tree.view()
        return tree
    return methodparse


class CountingVisitor(RPythonVisitor):
    def __init__(self):
        self.counts = {}

    def general_nonterminal_visit(self, node):
        print node.symbol
        self.counts[node.symbol] = self.counts.get(node.symbol, 0) + 1
        for child in node.children:
            self.dispatch(child)

    def general_symbol_visit(self, node):
        self.counts[node.symbol] = self.counts.get(node.symbol, 0) + 1


class BaseGrammarTest(object):
    def setup_class(cls):
        cls.parse = parse_func()


class TestLiterals(BaseGrammarTest):
    def setup_class(cls):
        cls.parse = parse_func('literal')

    def test_numbers(self):
        for i in range(10):
            dc = CountingVisitor()
            self.parse(str(i)).visit(dc)
            assert dc.counts["DECIMALLITERAL"] == 1


class IntEvaluationVisitor(RPythonVisitor):
    def general_symbol_visit(self, node):
        return node.additional_info

    def visit_DECIMALLITERAL(self, node):
        return int(node.additional_info)

    def general_nonterminal_visit(self, node):
        if len(node.children) == 1:
            return self.dispatch(node.children[0])
        if len(node.children) >= 3:
            code = [str(self.dispatch(child)) for child in node.children]
            while len(code) >= 3:
                r = self.evalop(int(code.pop(0)), code.pop(0), int(code.pop(0)))
                code.insert(0, r)
            return code[0]

    def visit_unaryexpression(self, node):
        if len(node.children) == 1:
            return self.dispatch(node.children[0])
        else:
            arg1 = self.dispatch(node.children[1])
            op = self.dispatch(node.children[0])
            return self.evalop(arg1, op)

    opmap = {'+': lambda x,y: x+y,
            '-': lambda x,y: x-y,
            '*': lambda x,y: x*y,
            '++': lambda x,y: x+1,
            '--': lambda x,y: x-1,
            '!': lambda x,y: not x,
            '~': lambda x,y: ~ x,
            '/': lambda x,y: x / y,
            '>>': lambda x,y: x>>y,
            '<<': lambda x,y: x<<y,
            '&': lambda x,y: x&y,
            '|': lambda x,y: x|y,
            '^': lambda x,y: x^y,
            '%': lambda x,y: x%y,
    }

    def evalop(self, arg1, op, arg2=None):
        return self.opmap[op](arg1, arg2)



class TestExpressions(BaseGrammarTest):
    def setup_class(cls):
        cls.parse = parse_func('expression')
        cls.evaluator = IntEvaluationVisitor()

    def parse_and_evaluate(self, s):
        tree = self.parse(s)
        result1 = self.evaluator.dispatch(tree)
        result2 = eval(s)
        assert result1 == result2
        return tree

    def parse_and_compare(self, s, n):
        tree = self.parse(s)
        result1 = self.evaluator.dispatch(tree)
        assert result1 == n
        return tree

    def parse_and_eval_all(self, l):
        for i in l:
            self.parse_and_evaluate(i)

    def test_simple(self):
        self.parse_and_eval_all(["1",
                        "1 + 2",
                        "1 - 2",
                        "1 * 2",
                        "1 / 2",
                        "1 >> 2",
                        "4 % 2",
                        "4 | 1",
                        "4 ^ 2",
        ])
        self.parse_and_compare("++5", 6)
        self.parse_and_compare("~3", -4)
        self.parse("x = 3")
        self.parse("x")

    def test_chained(self):
        self.parse_and_eval_all(["1 + 2 * 3",
                        "1 * 2 + 3",
                        "1 - 3 - 3",
                        "4 / 2 / 2",
                        "2 << 4 << 4",
                        "30 | 3 & 5",
        ])

    def test_primary(self):
        self.parse('this')
        self.parse('(x)')
        self.parse('((((x))))')
        self.parse('(x * (x * x)) + x - x')

    def test_array_literal(self):
        self.parse('[1,2,3,4]')
        self.parse('[1,2,]')
        self.parse('[1]')

    def test_object_literal(self):
        self.parse('{}')
        self.parse('{x:1}') #per spec {x:1,} should not be supported
        self.parse('{x:1,y:2}')

class TestStatements(BaseGrammarTest):
    def setup_class(cls):
        cls.parse = parse_func('statement')

    def parse_count(self, s):
        "parse the expression and return the CountingVisitor"
        cv = CountingVisitor()
        self.parse(s).visit(cv)
        return cv.counts

    def test_block(self):
        r = self.parse_count("{x;return;true;if(x);}")
        assert r['block'] == 1

    def test_vardecl(self):
        r = self.parse_count("var x;")
        assert r['variablestatement'] == 1

        r = self.parse_count("var x = 2;")
        assert r['variablestatement'] == 1

    def test_empty(self):
        self.parse(";")
        for i in range(1,10):
            r = self.parse_count('{%s}'%(';'*i))
            assert r['emptystatement'] == i

    def test_if(self):
        r = self.parse_count("if(x)return;")
        assert r['ifstatement'] == 1
        assert r.get('emptystatement', 0) == 0
        r = self.parse_count("if(x)if(i)return;")
        assert r['ifstatement'] == 2
        r = self.parse_count("if(x)return;else return;")
        assert r['ifstatement'] == 1

    def test_iteration(self):
        self.parse('for(;;);')
        self.parse('for(x;;);')
        self.parse('for(;x>0;);')
        self.parse('for(;;x++);')
        self.parse('for(var x = 1;;);')
        self.parse('for(x in z);')
        self.parse('for(var x in z);')
        self.parse('while(1);')
        self.parse('do ; while(1)')

    def test_continue_return_break_throw(self):
        self.parse('return;')
        self.parse('return x+y;')
        self.parse('break;')
        self.parse('continue;')
        self.parse('break label;')
        self.parse('continue label;')
        self.parse('throw (5+5);')

    def test_with(self):
        self.parse('with(x);')

    def test_labeled(self):
        self.parse('label: x+y;')

    def test_switch(self):
        self.parse("""switch(x) {
            case 1: break;
            case 2: break;
            default: ;
        }

        """)
        self.parse("""switch(x) {
            case 1: break;
            case 2: break;
            default: ;
            case 3: break;
        }

        """)
    def test_try(self):
        self.parse('try {x;} catch (e) {x;}')
        self.parse('try {x;} catch (e) {x;} finally {x;}')
        self.parse('try {x;} finally {x;}')

class TestFunctionDeclaration(BaseGrammarTest):
    def setup_class(cls):
        cls.parse = parse_func('functiondeclaration')

    def test_simpledecl(self):
        self.parse('function x () {;}')
        self.parse('function z (a,b,c,d,e) {;}')


class BaseTestToAST(BaseGrammarTest):
    def to_ast(self, s):
        return ASTBuilder().dispatch(self.parse(s))

    def compile(self, s):
        ast = self.to_ast(s)
        bytecode = JsCode()
        ast.emit(bytecode)
        return bytecode

    def check(self, source, expected):
        bytecode = self.compile(source)
        assert_bytecode_list_eql(bytecode.opcodes, expected)
        return bytecode

def assert_bytecode_list_eql(opcodes, list_of_opcodes):
    assert isinstance(list_of_opcodes, list)
    assert len(list_of_opcodes) == len(opcodes)
    for i, j in zip(opcodes, list_of_opcodes):
        assert repr(i) == j

class TestToASTExpr(BaseTestToAST):
    def setup_class(cls):
        cls.parse = parse_func('expression')

    def test_get_pos(self):
        from js import operations
        from rpython.rlib.parsing.tree import Symbol
        astb = ASTBuilder()
        t = self.parse('6')
        assert isinstance(t, Symbol)
        pos = astb.get_pos(t)
        assert pos.lineno == 0
        t = self.parse('[1,]')
        assert not isinstance(t, Symbol)
        pos = astb.get_pos(t)
        assert pos.start == 0

    @xfail
    def test_primaryexpression(self):
        self.check('(6)', ['LOAD_INTCONSTANT 6'])
        self.check('((((6))))', ['LOAD_INTCONSTANT 6'])
        self.check('x', ['LOAD_VARIABLE "x"'])
        self.check('[1,2,3.3,"abc"]', [
            'LOAD_INTCONSTANT 1',
            'LOAD_INTCONSTANT 2',
            'LOAD_FLOATCONSTANT 3.3',
            'LOAD_STRINGCONSTANT "abc"',
            'LOAD_ARRAY 4'])
        self.check('x[3] = 3', [
            'LOAD_INTCONSTANT 3',
            'LOAD_INTCONSTANT 3',
            'LOAD_VARIABLE "x"',
            'STORE_MEMBER'])
        self.check('x.x = 3', [
            'LOAD_INTCONSTANT 3',
            'LOAD_STRINGCONSTANT "x"',
            'LOAD_VARIABLE "x"',
            'STORE_MEMBER'])
        self.check('x = 3', [
            'LOAD_INTCONSTANT 3',
            'STORE "x"'])
        self.check('{"x":1}', [
            'LOAD_INTCONSTANT 1',
            'LOAD_STRINGCONSTANT "x"',
            "LOAD_OBJECT 1"])

    def test_raising(self):
        py.test.raises(FakeParseError, self.check, '1=2', [])

    @xfail
    def test_expression(self):
        self.check('1 - 1 - 1', [
            'LOAD_INTCONSTANT 1',
            'LOAD_INTCONSTANT 1',
            'SUB',
            'LOAD_INTCONSTANT 1',
            'SUB'])
        self.check('-(6 * (6 * 6)) + 6 - 6', [
            'LOAD_INTCONSTANT 6',
            'LOAD_INTCONSTANT 6',
            'LOAD_INTCONSTANT 6',
            'MUL',
            'MUL',
            'UMINUS',
            'LOAD_INTCONSTANT 6',
            'ADD',
            'LOAD_INTCONSTANT 6',
            'SUB'])
        py.test.raises(FakeParseError, self.check, '++5', [])
        py.test.raises(FakeParseError, self.check, '--5', [])
        self.check('"hello " + \'world\'',
                   ['LOAD_STRINGCONSTANT "hello "',
                    'LOAD_STRINGCONSTANT "world"',
                    'ADD'])

    @xfail
    def test_member(self):
        self.check('a["b"]',
                   ['LOAD_STRINGCONSTANT "b"',
                    'LOAD_VARIABLE "a"',
                    'LOAD_MEMBER'])

    @xfail
    def test_store_local(self):
        self.check("function f() {var x; x = 1;}",
            ['DECLARE_FUNCTION f [] [\n  DECLARE_VAR "x"\n  LOAD_INTCONSTANT 1\n  STORE_LOCAL 0\n]'])
        self.check("function f() {var x = 1;}",
            ['DECLARE_FUNCTION f [] [\n  DECLARE_VAR "x"\n  LOAD_INTCONSTANT 1\n  STORE_LOCAL 0\n]'])
        self.check('function f() {var x = 1; y = 2;}',
            ['DECLARE_FUNCTION f [] [\n  DECLARE_VAR "x"\n  LOAD_INTCONSTANT 1\n  STORE_LOCAL 0\n  POP\n  LOAD_INTCONSTANT 2\n  STORE "y"\n]'])

class TestToAstStatement(BaseTestToAST):
    def setup_class(cls):
        cls.parse = parse_func('statement')

    def check_remove_label(self, s, expected, expected_after_rl):
        bytecode = self.check(s, expected)
        bytecode.remove_labels()
        assert_bytecode_list_eql(bytecode.opcodes, expected_after_rl)

    @xfail
    def test_control_flow(self):
        self.check_remove_label('while (i>1) {x}',
                   ['LABEL 0',
                    'LOAD_VARIABLE "i"',
                    'LOAD_INTCONSTANT 1',
                    'GT',
                    'JUMP_IF_FALSE 1',
                    'LOAD_VARIABLE "x"',
                    'POP',
                    'JUMP 0',
                    'LABEL 1'],
                   ['LOAD_VARIABLE "i"',
                    'LOAD_INTCONSTANT 1',
                    'GT',
                    'JUMP_IF_FALSE 7',
                    'LOAD_VARIABLE "x"',
                    'POP',
                    'JUMP 0'])
        self.check_remove_label('if (x<3) {x} else {y}',[
                                'LOAD_VARIABLE "x"',
                                'LOAD_INTCONSTANT 3',
                                'LT',
                                'JUMP_IF_FALSE 0',
                                'LOAD_VARIABLE "x"',
                                'POP',
                                'JUMP 1',
                                'LABEL 0',
                                'LOAD_VARIABLE "y"',
                                'POP',
                                'LABEL 1'],[
                                'LOAD_VARIABLE "x"',
                                'LOAD_INTCONSTANT 3',
                                'LT',
                                'JUMP_IF_FALSE 7',
                                'LOAD_VARIABLE "x"',
                                'POP',
                                'JUMP 9',
                                'LOAD_VARIABLE "y"',
                                'POP'])
        self.check_remove_label('if (x) {y}',[
                                'LOAD_VARIABLE "x"',
                                'JUMP_IF_FALSE 0',
                                'LOAD_VARIABLE "y"',
                                'POP',
                                'LABEL 0'],[
                                'LOAD_VARIABLE "x"',
                                'JUMP_IF_FALSE 4',
                                'LOAD_VARIABLE "y"',
                                'POP'])
        self.check_remove_label('do { stuff } while (x)',[
                                'LABEL 0',
                                'LOAD_VARIABLE "stuff"',
                                'POP',
                                'LOAD_VARIABLE "x"',
                                'JUMP_IF_TRUE 0',
                                'LABEL 1'],[
                                'LOAD_VARIABLE "stuff"',
                                'POP',
                                'LOAD_VARIABLE "x"',
                                'JUMP_IF_TRUE 0'])

class TestToAstFunction(BaseTestToAST):
    def setup_class(cls):
        cls.parse = parse_func('sourceelements')

    @xfail
    def test_function_decl(self):
        self.check('function f(x, y, z) {x;}',
                   ['DECLARE_FUNCTION f [\'x\', \'y\', \'z\'] [\n  LOAD_LOCAL 0\n]'])

    @xfail
    def test_function_expression(self):
        self.check('var x = function() {return x}',[
            'DECLARE_VAR "x"',
            'DECLARE_FUNCTION [] [\n  LOAD_VARIABLE "x"\n  RETURN\n  LOAD_UNDEFINED\n]',
            'LOAD_FUNCTION',
            'STORE "x"',
            'POP'])

    @xfail
    def test_var_declr(self):
        self.check('x; var x;', [
            'DECLARE_VAR "x"',
            'LOAD_VARIABLE "x"',
            'POP'])

    @xfail
    def test_call(self):
        self.check('print("stuff")',[
            'LOAD_STRINGCONSTANT "stuff"',
            'LOAD_LIST 1',
            'LOAD_VARIABLE "print"',
            'CALL',
            'POP'])

    @xfail
    def test_member(self):
        self.check('a.b', ['LOAD_STRINGCONSTANT "b"',
                           'LOAD_VARIABLE "a"',
                           'LOAD_MEMBER',
                           'POP'])
        self.check('a.b = 3', ['LOAD_INTCONSTANT 3',
                               'LOAD_STRINGCONSTANT "b"',
                               'LOAD_VARIABLE "a"',
                               'STORE_MEMBER',
                               'POP'])

    @xfail
    def test_different_assignments(self):
        self.check('x += y', [
            'LOAD_VARIABLE "x"',
            'LOAD_VARIABLE "y"',
            'ADD',
            'STORE "x"',
            'POP'])
        self.check('x++', [
            'LOAD_VARIABLE "x"',
            'DUP',
            'INCR',
            'STORE "x"',
            'POP',
            'POP'])
        self.check('x.y++', [
            'LOAD_STRINGCONSTANT "y"',
            'LOAD_VARIABLE "x"',
            'LOAD_MEMBER',
            'DUP',
            'INCR',
            'LOAD_STRINGCONSTANT "y"',
            'LOAD_VARIABLE "x"',
            'STORE_MEMBER',
            'POP',
            'POP'])
        self.check('++x[2]', [
            'LOAD_INTCONSTANT 2',
            'LOAD_VARIABLE "x"',
            'LOAD_MEMBER',
            'INCR',
            'LOAD_INTCONSTANT 2',
            'LOAD_VARIABLE "x"',
            'STORE_MEMBER',
            'POP'])
        self.check('x.y -= 2',
                   ['LOAD_STRINGCONSTANT "y"',
                    'LOAD_VARIABLE "x"',
                    'LOAD_MEMBER',
                    'LOAD_INTCONSTANT 2',
                    'SUB',
                    'LOAD_STRINGCONSTANT "y"',
                    'LOAD_VARIABLE "x"',
                    'STORE_MEMBER',
                    'POP'])

    @xfail
    def test_variable_assign(self):
        self.check('x=1;', ['LOAD_INTCONSTANT 1', 'STORE "x"', 'POP'])
        self.check('var x; x = 1;', ['DECLARE_VAR "x"', 'LOAD_INTCONSTANT 1', 'STORE "x"', 'POP'])
        self.check('var x=1;', ['DECLARE_VAR "x"', 'LOAD_INTCONSTANT 1', 'STORE "x"', 'POP'])
        self.check('x+=1;', ['LOAD_VARIABLE "x"','LOAD_INTCONSTANT 1', 'ADD', 'STORE "x"', 'POP'])

    @xfail
    def test_local_function_param(self):
        self.check('function f(x) { return x; };', ['DECLARE_FUNCTION f [\'x\'] [\n  LOAD_LOCAL 0\n  RETURN\n  LOAD_UNDEFINED\n]'])
        self.check('function f(x) { var y; return y; };', ['DECLARE_FUNCTION f [\'x\'] [\n  DECLARE_VAR "y"\n  LOAD_LOCAL 1\n  RETURN\n  LOAD_UNDEFINED\n]'])
        self.check('function f(x) { return y; };', ['DECLARE_FUNCTION f [\'x\'] [\n  LOAD_VARIABLE "y"\n  RETURN\n  LOAD_UNDEFINED\n]'])

@xfail
def test_retlast_pop_removal():
    jscode = JsCode()
    jscode.emit('POP')
    jsfunc = jscode.make_js_function()
    assert not jsfunc.opcodes

    jscode = JsCode()
    jscode.emit('POP')
    jscode.emit('LABEL', 0)
    jsfunc = jscode.make_js_function()
    assert_bytecode_list_eql(jsfunc.opcodes, ['POP', 'LOAD_UNDEFINED'])


@xfail
def test_retlast_undefined_addition():
    jscode = JsCode()
    jsfunc = jscode.make_js_function()
    assert_bytecode_list_eql(jsfunc.opcodes, ['LOAD_UNDEFINED'])

    jscode = JsCode()
    jscode.emit('LOAD_INTCONSTANT', 1)
    jsfunc = jscode.make_js_function()
    assert_bytecode_list_eql(jsfunc.opcodes, ['LOAD_INTCONSTANT 1', 'LOAD_UNDEFINED'])

from js.jsparser import parse

@xfail
def test_simplesemicolon():
    yield parse, 'x'
    yield parse, 'if(1){x}'
    yield parse, 'function x () {}'
    yield parse,'if(1) {}'
