import re
from obin.types import space
from obin.compile.parse import tokens

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
    """ A simple regex-based lexer/tokenizer.

        See below for an example of usage.
    """
    def __init__(self, rules, skip_whitespace):
        """ Create a lexer.

            rules:
                A list of rules. Each rule is a `regex, type`
                pair, where `regex` is the regular expression used
                to recognize the token and `type` is the type
                of the token to return when it's recognized.

            skip_whitespace:
                If True, whitespace (\s+) will be skipped and not
                reported by the lexer. Otherwise, you have to
                specify your rules for whitespace, or it will be
                flagged as an error.
        """
        # All the regexes are concatenated into a single one
        # with named groups. Since the group names must be valid
        # Python identifiers, but the token types used by the
        # user are arbitrary strings, we auto-generate the group
        # names and map them to token types.
        #
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

    def tokens(self):
        """ Returns an iterator to the tokens found in the buffer.
        """
        while 1:
            tok = self.token()
            if tok is None:
                # ADD FAKE NEWLINE TO SUPPORT ONE LINE SCRIPT FILES
                yield tokens.newtoken(tokens.TT_NEWLINE, "\n", space.newint(-1), space.newint(-1), space.newint(1))
                yield tokens.newtoken(tokens.TT_ENDSTREAM, "", space.newint(-1), space.newint(-1), space.newint(1))
                break
            yield tok

    def _update_pos(self, match):
        self.pos = match.end()
        start = match.start()
        end = self.pos
        assert start >= 0
        assert end >= 1

        count = self.buf.count("\n", start, end)
        self.linecount = self.linecount + count
        last_nl = self.buf.rfind("\n", 0, start)
        if last_nl < 0:
            return start + 1
        else:
            return start - last_nl
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
            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                start,end = m.span(0)
                tok_type = self.group_type[groupname]
                # print tokens.token_type_to_s(tok_type), m.group(groupname), self.pos, m.start(), m.end(), start, end

                start = self.pos
                line = self.linecount
                col = self._update_pos(m)
                tok = tokens.newtoken(tok_type, m.group(groupname),
                                        space.newint(start),
                                        space.newint(line), space.newint(col))
                if tok_type == -1:
                    return self.token()

                return tok

            # if we're here, no rule matched
            raise(UnknownTokenError(self.pos))

##


def lexer(txt):
    lx = Lexer(tokens.RULES, False)
    lx.input(txt)
    return lx