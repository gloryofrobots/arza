from rply.errors import LexingError
from rply.token import SourcePosition, Token


class Lexer(object):
    def __init__(self, rules, ignore_rules):
        self.rules = rules
        self.ignore_rules = ignore_rules

    def lex(self, s):
        return LexerStream(self, s)


class LexerStream(object):
    def __init__(self, lexer, s):
        self.lexer = lexer
        self.s = s
        self.idx = 0

        self._lineno = 1

    def __iter__(self):
        return self

    def _update_pos(self, match):
        self.idx = match.end
        start = match.start
        end = match.end
        assert start >= 0
        assert end >= 1

        count = self.s.count("\n", start, end)
        self._lineno = self._lineno + count
        last_nl = self.s.rfind("\n", 0, start)
        if last_nl < 0:
            return start + 1
        else:
            return start - last_nl

    def next(self):
        if self.idx >= len(self.s):
            raise StopIteration
        for rule in self.lexer.ignore_rules:
            match = rule.matches(self.s, self.idx)
            if match:
                self._update_pos(match)
                return self.next()
        # print self.s[self.idx:]
        for rule in self.lexer.rules:
            match = rule.matches(self.s, self.idx)
            if match:
                start = match.start
                end = match.end
                assert start >= 0
                assert end >= 1

                lineno = self._lineno
                colno = self._update_pos(match)
                source_pos = SourcePosition(start, lineno, colno)
                token = Token(
                    rule.name, self.s[start:end], source_pos
                )
                return token
        else:
            raise LexingError(None, SourcePosition(self.idx, -1, -1))

    def __next__(self):
        return self.next()
