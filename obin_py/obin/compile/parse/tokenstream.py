from obin.compile.parse.token_type import TT_NEWLINE
from obin.compile.parse import nodes
from obin.compile.parse import tokens




class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.node = None
        self.token = None
        self.is_newline_occurred = False
        self.src = src

    def next(self):
        token = self.tokens.next()

        if tokens.token_type(token) == TT_NEWLINE:
            # print "NEW LINE"
            self.is_newline_occurred = True
            while tokens.token_type(token) == TT_NEWLINE:
                token = self.tokens.next()
        else:
            # print "TOKEN"
            self.is_newline_occurred = False

        # print token
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node


# if you choose to use ident based syntax choose this one
class TokenStream2:
    def __init__(self, _tokens, src):
        self.tokens = [token for token in _tokens]
        self.index = 0
        self.length = len(self.tokens)
        self.node = None
        self.token = None
        self.is_newline_occurred = False
        self.src = src

    def _next(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    def next(self):
        if self.index >= self.length:
            return self.node

        token = self._next()

        if tokens.token_type(token) == TT_NEWLINE:
            # print "NEW LINE"
            self.is_newline_occurred = True
            while tokens.token_type(token) == TT_NEWLINE:
                token = self._next()
        else:
            # print "TOKEN"
            self.is_newline_occurred = False

        # print token
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node
