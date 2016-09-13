__author__ = 'gloryofrobots'
from arza.compile.parse.rply.lexergenerator import LexerGenerator
from arza.compile.parse import tokens
from arza.types import space


def create_generator(rules):
    lg = LexerGenerator()
    for rule in rules:
        lg.add(rule[1], rule[0])
    lexer = lg.build()
    return lexer


class UnknownTokenError(Exception):
    def __init__(self, position):
        self.position = position


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
        from arza.compile.parse.rply.lexer import LexingError
        try:
            return self._token()
        except StopIteration:
            return None
        except LexingError as e:
            pos = e.source_pos
            raise (UnknownTokenError(pos.idx))

    def _token(self):
        t = next(self.stream)
        # print tokens.token_type_to_str(t.name), t.value
        token = tokens.newtoken(t.name, t.value,
                                space.newint(t.source_pos.idx),
                                space.newint(t.source_pos.lineno), space.newint(t.source_pos.colno))
        if tokens.token_type(token) == -1:
            return self._token()

        return token

    def tokens(self):
        """ Returns an iterator to the tokens found in the buffer.
        """
        while 1:
            tok = self.token()
            if tok is None:
                # ADD FAKE NEWLINE TO SUPPORT ONE LINE SCRIPT FILES
                yield tokens.newtoken(tokens.TT_ENDSTREAM, "", space.newint(-1), space.newint(-1), space.newint(1))
                break
            yield tok


##


def lexer(txt):
    lx = Lexer(tokens.RULES, False)
    lx.input(txt)
    return lx
