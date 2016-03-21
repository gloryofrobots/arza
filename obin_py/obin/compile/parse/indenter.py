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

        # CHECK FIRST TOKEN HERE BECAUSE TRAILING SPACE AT FIRST LINE ARE IGNORED
        # IT HAPPENS BECAUSE TT_INDENTATION IS PARSED as \n[ ]*
        if self.has_tokens():
            first = self.tokens[0]
            if api.to_i(tokens.token_column(first)) != 1:
                indentation_error(u"First line indented", first)

        self.index = 0
        self.length = len(self.tokens)
        self.node = None
        self.token = None
        self.src = src
        self.generated_tokens = []
        self.blocks = plist.empty()
        self.add_top_level_block()

    def current_block(self):
        return plist.head(self.blocks)

    def _add_block(self, block):
        print "ADD BLOCK", block
        self.blocks = plist.cons(block, self.blocks)

    def pop_block(self):
        self.blocks = plist.tail(self.blocks)

    def has_tokens(self):
        return len(self.tokens) > 0

    def has_blocks(self):
        return plist.is_empty(self.blocks)

    def add_top_level_block(self):
        self._add_block(Block(-1, 0, False, False, False))

    def add_nested_code_block(self):
        cur = self.current_block()
        self._add_block(Block(cur.level, -1, False, True, False))

    def add_code_block(self):
        cur = self.current_block()
        self._add_block(Block(cur.level, -1, True, True, False))

    def add_free_block(self):
        cur = self.current_block()
        self._add_block(Block(cur.level, api.to_i(tokens.token_column(self.token)), False, False, True))

    def add_to_generated(self, token):
        self.generated_tokens.append(token)

    def next_generated(self):
        token = self.generated_tokens.pop()
        print "NEXT GENERATED TOKEN", tokens.token_to_s(token)
        return self.attach_token(token)

    def has_generated(self):
        return len(self.generated_tokens) != 0

    def _next(self):
        token = self.tokens[self.index]
        print "NEXT STREAM TOKEN", tokens.token_to_s(token)
        self.index += 1
        return token

    def _whats_next(self):
        return tokens.token_type(self.tokens[self.index])

    def _on_indentation(self, token):
        while self._whats_next() == tt.TT_INDENTATION:
            print "SKIP"
            token = self._next()
        # subtract \n from spaces
        level = len(tokens.token_value_s(token)) - 1
        block = self.current_block()
        # new uninitialized block
        # FIXME IT WILL BROKE COMBINED APPROACH when if x == 1 -> somecode \n somecode
        if block.level == -1:
            if level <= block.parent_level:
                return indentation_error(u"Indentation level must be <= then parent level", token)
            block.level = level
            # if block.push_end_of_expression_on_new_line is True:
            #     self.add_to_generated(tokens.create_end_expression_token(token))
            return self.next()

        # new free block
        if block.ignore_new_lines is True:
            if level <= block.parent_level:
                return indentation_error(u"Indentation level of free block must be lesser then of parent block",
                                         token)
            return self.next()


        if level > block.level:
            return indentation_error(u"Invalid indentation level", token)

        # dedent
        blocks = self.blocks
        while True:
            block = plist.head(blocks)
            blocks = plist.tail(blocks)
            if space.isvoid(block):
                return indentation_error(u"Indentation does not match with any of previous levels", token)

            if block.level < level:
                return indentation_error(u"Invalid indentation level", token)
            elif block.level > level:
                # if block.push_end_of_expression_on_new_line is True:
                #     self.add_to_generated(tokens.create_end_expression_token(token))
                if block.push_end_on_dedent is True:
                    self.add_to_generated(tokens.create_end_token(token))
            elif block.level == level:
                if block.push_end_of_expression_on_new_line is True:
                    self.add_to_generated(tokens.create_end_expression_token(token))

                return self.next()
            self.blocks = blocks

    def attach_token(self, token):
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node

    def next(self):
        if self.has_generated():
            return self.next_generated()

        if self.index >= self.length:
            return self.node

        token = self._next()
        ttype = tokens.token_type(token)
        if ttype == tt.TT_INDENTATION:
            return self._on_indentation(token)
        elif ttype == tt.TT_END:
            self.pop_block()
            if self.has_blocks():
                indentation_error(u"End keyword without an block", token)

        return self.attach_token(token)
