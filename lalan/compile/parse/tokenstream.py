from lalan.compile.parse.token_type import TT_NEWLINE, TT_ENDSTREAM
from lalan.compile.parse import nodes

DEBUG = False


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
        self.is_newline_occurred = False

    def push_encloser(self, token):
        self.enclosers.append([token, False])
        log("push_encloser %s ", self.enclosers)

    def pop_encloser(self):
        assert self.get_encloser_level() == 0, self.get_encloser_level()
        self.enclosers.pop()
        log("pop_encloser %s ", self.enclosers)

    # def mark_encloser(self):
    #     m = self.enclosers[-1][1]
    #     if not m:
    #         self.enclosers[-1][1] = True
    #     return m

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
        self.node = nodes.node_blank(self.token)
        return self.node

