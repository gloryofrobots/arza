__author__ = 'gloryofrobots'
from rply import LexerGenerator
from obin.compile.parse import tokens
from obin.compile.parse.token_type import *

def create_generator(rules):
    lg = LexerGenerator()
    for rule in rules:
        lg.add(rule[1], rule[0])
    lexer = lg.build()
    return lexer


class UnknownTokenError(Exception):
    def __init__(self, position):
        self.position = position

class Token:
    """ A simple Token structure.
        Contains the token type, value and position.
    """

    def __init__(self, type, val, pos, line, column):
        assert isinstance(type, int)
        assert isinstance(val, str)
        assert isinstance(pos, int)
        assert isinstance(line, int)
        self.type = type
        self.val = val
        self.pos = pos
        self.line = line
        self.column = column

    def __str__(self):
        try:
            t_repr = tokens.token_type_to_str(self.type)
        except:
            t_repr = self.type

        if self.type == tokens.TT_NEWLINE:
            val = '\\n'
        else:
            val = self.val

        return '<%s %s %d:%d>' % (t_repr, val, self.line, self.pos)


class LexerError(Exception):
    """ Lexer error exception.

        pos:
            Position in the input line where the error occurred.
    """

    def __init__(self, pos):
        self.pos = pos


class Lexer:

    def __init__(self, rules, skip_whitespace):
        assert isinstance(rules, list)
        assert isinstance(skip_whitespace, bool)

        self.lexer = create_generator(rules)
        self.stream = None

    def input(self, buf):
        self.stream = self.lexer.lex(buf)

    def token(self):
        """ Return the next token (a Token object) found in the
            input buffer. None is returned if the end of the
            buffer was reached.
            In case of a lexing error (the current chunk of the
            buffer matches no rule), a LexerError is raised with
            the position of the error.
        """
        from rply.lexer import LexingError
        try:
            return self._token()
        except StopIteration:
            return None
        except LexingError as e:
            pos = e.source_pos
            raise(UnknownTokenError(pos.idx))

    def _token(self):
        t = next(self.stream)
        # print tokens.token_type_to_str(t.name), t.value
        token = Token(t.name, t.value, t.source_pos.idx, t.source_pos.lineno, t.source_pos.colno)
        if token.type == -1:
            return self._token()

        return token

    def tokens(self):
        """ Returns an iterator to the tokens found in the buffer.
        """
        while 1:
            tok = self.token()
            if tok is None:
                yield Token(tokens.TT_ENDSTREAM, "", 0, 0, 0)
                break
            yield tok


##


def lexer(txt):
    lx = Lexer(tokens.RULES, False)
    lx.input(txt)
    return lx
