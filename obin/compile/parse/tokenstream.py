from obin.compile.parse.token_type import TT_NEWLINE
from obin.compile.parse import nodes
from obin.compile.parse import tokens


class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.node = None
        self.token = None
        self.src = src

    def next_token(self):
        token = self.tokens.next()
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node
