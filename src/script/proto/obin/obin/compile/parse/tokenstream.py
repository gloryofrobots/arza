from obin.compile.parse.token_type import TT_NEWLINE
from obin.compile.parse.nodes import Node




class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.node = None
        self.token = None
        self.is_newline_occurred = False
        self.src = src

    def next(self):
        token = self.tokens.next()

        if token.type == TT_NEWLINE:
            # print "NEW LINE"
            self.is_newline_occurred = True
            while token.type == TT_NEWLINE:
                token = self.tokens.next()
        else:
            # print "TOKEN"
            self.is_newline_occurred = False

        # print token
        self.token = token
        self.node = Node(self.token)
        return self.node
