from arza.compile.parse.token_type import TT_NEWLINE
from arza.compile.parse import nodes


class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.token = None
        self.previous = None
        self.src = src

    def next_token(self):
        self.previous = self.token
        token = self.tokens.next()
        self.token = token
        return self.token
