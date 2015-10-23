__author__ = 'gloryofrobots'
from token_type import *
from obin.objects.symbol_map import SymbolMap
def _compile(ast, code, )


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

def compile(ast):

    pass