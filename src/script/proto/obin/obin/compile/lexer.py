import re
from obin.compile.parse import tokens


class Token:
    """ A simple Token structure.
        Contains the token type, value and position.
    """

    def __init__(self, type, val, pos, line):
        self.type = type
        self.val = val
        self.pos = pos
        self.line = line

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
    """ A simple regex-based lexer/tokenizer.

        See below for an example of usage.
    """

    def __init__(self, rules, skip_whitespace):
        # All the regexes are concatenated into a single one
        # with named groups. Since the group names must be valid
        # Python identifiers, but the token types used by the
        # user are arbitrary strings, we auto-generate the group
        # names and map them to token types.
        #
        assert isinstance(rules, list)
        assert isinstance(skip_whitespace, bool)

        self.linecount = 1

        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, type in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = type
            idx += 1

        pattern = '|'.join(regex_parts)
        # print pattern
        # print "*************************"
        self.regex = re.compile(pattern)
        self.skip_whitespace = skip_whitespace
        self.re_ws_skip = re.compile('\S')

    def input(self, buf):
        """ Initialize the lexer with a buffer as input.
        """
        self.buf = buf
        self.pos = 0

    def token(self):
        """ Return the next token (a Token object) found in the
            input buffer. None is returned if the end of the
            buffer was reached.
            In case of a lexing error (the current chunk of the
            buffer matches no rule), a LexerError is raised with
            the position of the error.
        """
        if self.pos >= len(self.buf):
            return None
        else:
            if self.skip_whitespace:
                m = self.re_ws_skip.search(self.buf, self.pos)

                if m:
                    self.pos = m.start()
                else:
                    return None

            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = Token(tok_type, m.group(groupname), self.pos, self.linecount)
                self.pos = m.end()
                if tok_type is -1:
                    return self.token()
                if tok.type == tokens.TT_NEWLINE:
                    self.linecount += 1

                return tok

            # if we're here, no rule matched
            raise LexerError(self.pos)

    def tokens(self):
        """ Returns an iterator to the tokens found in the buffer.
        """
        while 1:
            tok = self.token()
            if tok is None:
                yield Token(tokens.TT_ENDSTREAM, 0, 0, 0)
                break
            yield tok


##


def lexer(txt):
    lx = Lexer(tokens.RULES, False)
    lx.input(txt)
    return lx
