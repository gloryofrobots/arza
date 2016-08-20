from lalan.compile.parse.token_type import TT_NEWLINE, TT_ENDSTREAM
from lalan.compile.parse import nodes

DEBUG = True


def log(msg, *args):
    msg = msg % map(str, args)
    if DEBUG:
        print msg


class TokenStream:
    def __init__(self, _tokens, src):
        self.tokens = _tokens
        self.node = None
        self.token = None
        self.previous = None
        self.src = src
        self.enclosers = [[TT_ENDSTREAM, True]]

    def push_encloser(self, token):
        self.enclosers.append([token, 0])
        log("push_encloser %s ", self.enclosers)

    def pop_encloser(self):
        self.enclosers.pop()
        log("pop_encloser %s ", self.enclosers)


    def increment_encloser_level(self):
        self.enclosers[-1][1] += 1
        log("increment_encloser_level %s ", self.enclosers)

    def decrement_encloser_level(self):
        self.enclosers[-1][1] -= 1
        log("decrement_encloser_level %s ", self.enclosers)

    def get_encloser_level(self):
        return self.enclosers[-1][1]

    def get_encloser(self):
        return self.enclosers[-1][0]

    def next_token(self):
        self.previous = self.token
        token = self.tokens.next()
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node
