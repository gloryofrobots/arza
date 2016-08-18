from lalan.compile.parse.token_type import TT_NEWLINE
from lalan.compile.parse import nodes


class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.node = None
        self.token = None
        self.previous = None
        self.src = src

    def next_token(self):
        self.previous = self.token
        token = self.tokens.next()
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node
