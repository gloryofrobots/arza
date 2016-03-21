from obin.compile.parse import token_type as tt
from obin.compile.parse import nodes
from obin.compile.parse import tokens
from obin.types import api, space, plist, root


class InvalidIndentationError(Exception):
    def __init__(self, msg, position, line, column):
        self.position = position
        self.line = line
        self.column = column
        self.msg = msg

    def __str__(self):
        return self.msg


class Block(root.W_Root):
    def __init__(self, parent_level, level, push_end_on_dedent, push_end_of_expression_on_new_line, ignore_new_lines):
        self.parent_level = parent_level
        self.level = level
        self.push_end_on_dedent = push_end_on_dedent
        self.push_end_of_expression_on_new_line = push_end_of_expression_on_new_line
        self.ignore_new_lines = ignore_new_lines

    def _to_string_(self):
        return "<Block level %d %d %s %s %s>" % (self.parent_level, self.level, str(self.push_end_on_dedent),
                                                 str(self.push_end_of_expression_on_new_line),
                                                 str(self.ignore_new_lines))


def indentation_error(msg, token):
    raise InvalidIndentationError(msg,
                                  api.to_i(tokens.token_position(token)),
                                  api.to_i(tokens.token_line(token)),
                                  api.to_i(tokens.token_column(token)))


class IndentationTokenStream:
    def __init__(self, _tokens, src):
        self.tokens = [token for token in _tokens]

        self.index = 0
        self.length = len(self.tokens)
        self.node = None
        self.token = None
        self.src = src
        self.logical_tokens = []

        # first = self.tokens[0]
        # if api.to_i(tokens.token_column(first)) != 1:
        #     indentation_error(u"First line indented", first)

        level = self._find_level()
        self.blocks = plist.plist([Block(-1, level, False, False, False)])

    def current_block(self):
        return plist.head(self.blocks)

    def pop_block(self):
        self.blocks = plist.tail(self.blocks)

    def has_tokens(self):
        return len(self.tokens) > 0

    def has_blocks(self):
        return not plist.is_empty(self.blocks)

    def _find_level(self):
        token = self._advance_to_physical_token()
        return tokens.token_column_i(token) - 1

    def _add_block(self, push_end_on_dedent, push_end_of_expression_on_new_line, ignore_new_lines):
        cur = self.current_block()
        level = self._find_level()
        block = Block(cur.level, level, push_end_on_dedent, push_end_of_expression_on_new_line, ignore_new_lines)
        print "ADD BLOCK", block
        self.blocks = plist.cons(block, self.blocks)

    def add_nested_code_block(self):
        self._add_block(False, True, False)

    def add_code_block(self):
        self._add_block(True, True, False)

    def add_free_block(self):
        self._add_block(False, False, True)

    def add_logical_token(self, token):
        self.logical_tokens.append(token)

    def next_logical(self):
        token = self.logical_tokens.pop()
        print "NEXT LOGICAL TOKEN", tokens.token_to_s(token)
        return self.attach_token(token)

    def has_generated(self):
        return len(self.logical_tokens) != 0

    def next_physical(self):
        token = self.tokens[self.index]
        print "NEXT STREAM TOKEN", tokens.token_to_s(token)
        self.index += 1
        return token

    def _whats_next(self):
        return tokens.token_type(self.tokens[self.index])

    def _advance_to_physical_token(self):
        token = self.next_physical()
        while tokens.token_type(token) == tt.TT_NEWLINE:
            print "SKIP"
            token = self.next_physical()

        self.index -= 1
        return token

    def _on_indentation(self):
        token = self._advance_to_physical_token()
        level = tokens.token_column_i(token) - 1

        block = self.current_block()

        # new free block
        if block.ignore_new_lines is True:
            if level <= block.parent_level:
                return indentation_error(u"Indentation level of free block must be lesser then of parent block",
                                         token)
            return self.next()

        elif level > block.level:
            return indentation_error(u"Invalid indentation level", token)
        else:
            blocks = self.blocks
            while True:
                block = plist.head(blocks)
                blocks = plist.tail(blocks)
                if space.isvoid(block):
                    return indentation_error(u"Indentation does not match with any of previous levels", token)

                if block.level < level:
                    return indentation_error(u"Invalid indentation level", token)
                elif block.level > level:
                    self.on_dedent(block, token)
                elif block.level == level:
                    self.on_newline(block, token)
                    return self.next()
                self.blocks = blocks

    def on_newline(self, block, token):
        if block.push_end_of_expression_on_new_line is True:
            self.add_logical_token(tokens.create_end_expression_token(token))

    def on_dedent(self, block, token):
        if block.push_end_on_dedent is True:
            self.add_logical_token(tokens.create_end_token(token))
        elif block.push_end_of_expression_on_new_line is True:
            self.add_logical_token(tokens.create_end_expression_token(token))

    def attach_token(self, token):
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node

    def next(self):
        if self.has_generated():
            return self.next_logical()

        if self.index >= self.length:
            return self.node

        token = self.next_physical()
        ttype = tokens.token_type(token)
        if ttype == tt.TT_NEWLINE:
            return self._on_indentation()
        elif ttype == tt.TT_END:
            self.pop_block()
            if not self.has_blocks():
                indentation_error(u"End keyword without an block", token)

        return self.attach_token(token)
