from arza.compile.parse import token_type as tt
from arza.compile.parse import nodes
from arza.compile.parse import tokens
from arza.compile.parse import tokenstream
from arza.types import api, space, plist, root
from arza.misc.fifo import Fifo

LOG_INDENTER = api.DEBUG_MODE

MODULE = -1
NODE = 0
CODE = 1
OFFSIDE = 2
FREE = 3


def log(*args):
    if not LOG_INDENTER:
        return
    print ", ".join([str(arg) for arg in args])


def open_free_layout(parser, token, terminators, delimiter=None):
    ts = parser.ts
    ts.skip_newlines()
    return ts.add_layout(token, FREE, None, terminators, delimiter, None)


def open_statement_layout(parser, token, level_tokens, indentation_tokens):
    ts = parser.ts
    layout = ts.current_layout()
    if layout.is_free():
        if layout.statements_count > 0:
            return indentation_error(u"This code block must be enclosed in parentheses", token)

        layout.statements_count += 1
        return layout

    return ts.add_layout(token, OFFSIDE, level_tokens, None, None, indentation_tokens)


def open_offside_layout(parser, token, level_tokens, indentation_tokens):
    ts = parser.ts
    layout = ts.current_layout()
    if layout.is_free():
        return layout

    return ts.add_layout(token, OFFSIDE, level_tokens, None, None, indentation_tokens)


def open_code_layout(parser, token, level_tokens=None, terminators=None, indentation_tokens=None):
    ts = parser.ts
    layout = ts.current_layout()
    if layout.is_free():
        return layout
        # if terminators:
        #     return open_free_layout(parser, token, terminators, layout.delimiter)
        # else:
        #     return layout
    level = tokens.token_level(token)
    if level <= layout.level:
        return indentation_error(u"Code layout must be indented", token)

    return ts.add_layout(token, CODE, level_tokens, terminators, None, indentation_tokens)


class InvalidIndentationError(Exception):
    def __init__(self, msg, position, line, column):
        self.position = position
        self.line = line
        self.column = column
        self.msg = msg

    def __str__(self):
        return self.msg


class Layout(root.W_Root):
    def __init__(self, parent_level, line, level, type, level_tokens, terminators, delimiter, indentation_tokens):
        self.opened = True
        self.parent_level = parent_level
        self.line = line
        self.level = level
        self.type = type
        self.level_tokens = level_tokens if level_tokens else []
        self.indentation_tokens = indentation_tokens if indentation_tokens else []
        self.terminators = terminators if terminators else []
        self.delimiter = delimiter
        self.statements_count = 0

    def support_indentation(self, ttype):
        return ttype in self.indentation_tokens

    def has_level(self, token_type):
        return token_type in self.level_tokens

    def has_terminator(self, token_type):
        return token_type in self.terminators

    def has_level_tokens(self):
        return len(self.level_tokens) > 0

    def _to_string_(self):
        bt = self.type
        bt_s = None
        if bt == CODE:
            bt_s = "CODE"
        elif bt == FREE:
            bt_s = "FREE"
        elif bt == MODULE:
            bt_s = "MODULE"
        elif bt == NODE:
            bt_s = "NODE"
        elif bt == OFFSIDE:
            bt_s = "OFFSIDE"
        return "<Block plvl=%d, lvl=%d, line=%d, t=%s>" % (self.parent_level, self.level, self.line, bt_s)

    def is_code(self):
        return self.type == CODE

    def is_offside(self):
        return self.type == OFFSIDE

    def is_free(self):
        return self.type == FREE

    def is_module(self):
        return self.type == MODULE

    def is_open(self):
        return self.opened

    def close(self):
        self.opened = False


def indentation_error(msg, token):
    raise InvalidIndentationError(msg,
                                  api.to_i(tokens.token_position(token)),
                                  api.to_i(tokens.token_line(token)),
                                  api.to_i(tokens.token_column(token)))


class IndentationTokenStream(tokenstream.TokenStream):
    def __init__(self, lexer, src):
        _tokens = lexer.tokens()
        tokenstream.TokenStream.__init__(self, _tokens, src)

        self.lexer = lexer
        self.tokens = [token for token in _tokens]
        self.length = len(self.tokens)

        # if LOG_INDENTER:
        #     for token in self.tokens:
        #         print tokens.token_to_s(token)

        self.index = 0
        self.length = len(self.tokens)
        self.logical_tokens = Fifo()
        self.produced_tokens = []

        level = self._find_level()
        # self.layouts = plist.empty()

        self.layouts = plist.plist([Layout(-1, -1, level, MODULE, None, None, None, None)])
        self.indentation_token = None

    def advanced_values(self):
        t = [tokens.token_value_s(token) for token in self.produced_tokens]
        return " ".join(t)

    def current_layout(self):
        return plist.head(self.layouts)

    def next_layout(self):
        return plist.head(plist.tail(self.layouts))

    def pop_layout(self):
        old_layout = self.current_layout()
        self.layouts = plist.tail(self.layouts)
        old_layout.close()

        log("---- POP LAYOUT", old_layout)
        log(self.advanced_values())
        log(self.layouts)

        return self.current_layout()

    def _find_level(self):
        token = self.skip_newlines()
        return tokens.token_level(token)

    def add_layout(self, token, type, level_tokens, terminators,
                   delimiter, indentation_tokens):

        self.check_indentation_tokens(token)
        cur = self.current_layout()
        level = tokens.token_level(token)
        line = tokens.token_line_i(token)

        layout = Layout(cur.level, line, level, type, level_tokens, terminators, delimiter, indentation_tokens)

        self.layouts = plist.cons(layout, self.layouts)

        log("---- ADD LAYOUT", layout)
        log(self.advanced_values())
        log(self.layouts)

        return layout

    def check_indentation_tokens(self, token):
        if self.indentation_token is None:
            self.indentation_token = self.lexer.indentation
            return

        if self.indentation_token != self.lexer.indentation:
            return indentation_error(u"Tabs and spaces can not be used at he same time",
                                     token)


    def has_layouts(self):
        return not plist.is_empty(self.layouts)

    def count_layouts(self):
        return plist.length(self.layouts)

    def has_tokens(self):
        return len(self.tokens) > 0

    def has_logic_tokens(self):
        return not self.logical_tokens.is_empty()

    def add_logical_token(self, token):
        log("=*=* ADD LOGICAL", token)
        self.logical_tokens.append(token)

    def next_logical(self):
        token = self.logical_tokens.pop()
        # log("=*=* NEXT LOGICAL TOKEN", tokens.token_to_s(token))
        return self.attach_token(token)

    def has_next_token(self):
        return self.index < self.length

    def lookup_next_token(self):
        if not self.has_next_token():
            return indentation_error(u"Error evaluating next token",
                                     self.token)

        return self.tokens[self.index]

    def next_physical(self):
        if self.index == self.length:
            return self.tokens[self.length - 1]

        token = self.tokens[self.index]
        # log( "++++ NEXT STREAM TOKEN", tokens.token_to_s(token))
        self.index += 1
        return token

    # def _skip_indent(self):
    #     if not self.has_logic_tokens():
    #         return None
    #
    #     token = self.next_logical()
    #     while tokens.token_type(token) == tt.TT_INDENT:
    #         # log("++++ SKIP")
    #         token = self.next_logical()
    #
    #         if not self.has_logic_tokens():
    #             break
    #
    #     self.index -= 1
    #     return token

    def skip_newlines(self):
        token = self.next_physical()
        while tokens.token_type(token) == tt.TT_NEWLINE:
            # log("++++ SKIP")
            token = self.next_physical()

        self.index -= 1
        return token

    def current_physical(self):
        return self.tokens[self.index]

    def current_type(self):
        return tokens.token_type(self.token)

    def current_physical_type(self):
        return tokens.token_type(self.current_physical())

    def _on_newline(self):
        token = self.skip_newlines()
        self.check_indentation_tokens(token)
        return self._check_layout(token)

    def _check_layout(self, token):

        ttype = tokens.token_type(token)

        # if ttype == tt.TT_ENDSTREAM:
        #     1

        cur_type = self.current_type()

        layout = self.current_layout()
        level = tokens.token_level(token)
        log("----NEW LINE", level, layout, tokens.token_to_s(token))

        # TODO remove not layout.is_module() after implementing real pragmas ![]
        if not layout.is_free() or layout.is_module():
            if layout.support_indentation(cur_type):
                if level < layout.level:
                    return indentation_error(u"Indentation level of token next to"
                                             u" operator must be bigger then of parent layout",
                                             token)

                return self.next_token()

        # if tokens.is_infix_token_type(cur_type) and (not layout.is_free() or layout.is_module()):
        #     if level < layout.level:
        #         return indentation_error(u"Indentation level of token next to"
        #                                  u" operator must be bigger then of parent layout",
        #                                  token)
        #
        #     return self.next_token()

        if layout.is_free() is True:
            return self.next_token()

        if level > layout.level:
            if not layout.support_indentation(ttype):
                return indentation_error(u"Invalid indentation", token)

            return self.next_token()
        else:
            layouts = self.layouts
            while True:
                layout = plist.head(layouts)
                layouts = plist.tail(layouts)
                if space.isvoid(layout):
                    return indentation_error(u"Indentation does not match with any of previous levels", token)

                if layout.level == level:
                    if layout.is_offside():
                        if not layout.has_level(ttype):
                            self.pop_layout()
                    elif layout.is_code() and layout.has_level_tokens():
                        if not layout.has_level(ttype):
                            return indentation_error(u"Unexpected token at layout level", token)

                    return self.next_token()

                elif layout.level > level:
                    self.pop_layout()
                    # log("---- POP_LAYOUT", layout)
                    # log(self.advanced_values())
                    #
                    # self.layouts = layouts
                elif layout.level < level:
                    return indentation_error(u"Invalid indentation level", token)

    def attach_token(self, token):
        log("^^^^^ATTACH", tokens.token_to_s(token))
        self.token = token
        self.produced_tokens.append(self.token)
        return self.token

    # def next_token(self):
    #     token = self._next_token()
    #     ttype = tokens.token_type(token)
    #     layout = self.current_layout()
    #
    #     # if layout.is_free() and layout.has_terminator(ttype):
    #     #     self.pop_layout()
    #     if layout.has_terminator(ttype):
    #         self.pop_layout()
    #
    #     return token
    #
    # def _next_token(self):
    #     log(self.advanced_values())
    #     self.previous = self.token
    #     if self.has_logic_tokens():
    #         return self.next_logical()
    #
    #     if self.index >= self.length:
    #         return self.token
    #
    #     token = self.next_physical()
    #     ttype = tokens.token_type(token)
    #
    #     if ttype == tt.TT_NEWLINE:
    #         return self._on_newline()
    #     elif ttype == tt.TT_ENDSTREAM:
    #         if api.length_i(self.layouts) != 1:
    #             indentation_error(u"Not all layouts closed", token)
    #
    #     return self.attach_token(token)

    def next_token(self):
        log(self.advanced_values())
        self.previous = self.token
        if self.has_logic_tokens():
            return self.next_logical()

        if self.index >= self.length:
            return self.token

        token = self.next_physical()
        ttype = tokens.token_type(token)

        if ttype == tt.TT_NEWLINE:
            return self._on_newline()
        elif ttype == tt.TT_ENDSTREAM:
            # prev_type = tokens.token_type(self.previous)
            # if prev_type != tt.TT_NEWLINE:
            #     self._check_layout(token)
            if api.length_i(self.layouts) != 1:
                indentation_error(u"Not all layouts closed", token)

        layout = self.current_layout()

        # if layout.is_free() and layout.has_terminator(ttype):
        #     self.pop_layout()
        if layout.has_terminator(ttype):
            self.pop_layout()

        return self.attach_token(token)
