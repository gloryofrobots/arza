from obin.compile.parse import token_type as tt
from obin.compile.parse import nodes
from obin.compile.parse import tokens
from obin.types import api, space, plist, root
from obin.misc.fifo import Fifo

SKIP_NEWLINE_TOKENS = [tt.TT_JUXTAPOSITION, tt.TT_DOUBLE_COLON,
                       tt.TT_COLON, tt.TT_OPERATOR, tt.TT_DOT, tt.TT_ASSIGN]


class InvalidIndentationError(Exception):
    def __init__(self, msg, position, line, column):
        self.position = position
        self.line = line
        self.column = column
        self.msg = msg

    def __str__(self):
        return self.msg


MODULE = -1
NODE = 0
CHILD = 1
OFFSIDE = 2
FREE = 3


class Block(root.W_Root):
    def __init__(self, parent_level, level, type, level_tokens, terminators):
        self.parent_level = parent_level
        self.level = level
        self.type = type
        self.level_tokens = level_tokens if level_tokens else []
        self.terminators = terminators if terminators else []

    def has_level(self, token_type):
        return token_type in self.level_tokens

    def has_terminator(self, token_type):
        return token_type in self.terminators

    @property
    def push_end_of_expression_on_new_line(self):
        return self.type == CHILD or self.type == MODULE

    @property
    def push_end_on_dedent(self):
        return self.type == NODE

    @property
    def push_end_of_expression_on_dedent(self):
        return self.type == NODE

    def _to_string_(self):
        bt = self.type
        bt_s = None
        if bt == CHILD:
            bt_s = "CHILD"
        elif bt == FREE:
            bt_s = "FREE"
        elif bt == MODULE:
            bt_s = "MODULE"
        elif bt == NODE:
            bt_s = "NODE"
        elif bt == OFFSIDE:
            bt_s = "OFFSIDE"
        return "<Block pl=%d, l=%d, t=%s>" % (self.parent_level, self.level, bt_s)


    def is_child(self):
        return self.type == CHILD

    def is_node(self):
        return self.type == NODE

    def is_free(self):
        return self.type == FREE

    def is_module(self):
        return self.type == MODULE


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
        self.logical_tokens = Fifo()
        self.produced_tokens = []

        # first = self.tokens[0]
        # if api.to_i(tokens.token_column(first)) != 1:
        #     indentation_error(u"First line indented", first)
        # self.attach_token(self.tokens[0])
        level = self._find_level()
        self.blocks = plist.plist([Block(-1, level, MODULE, None, None)])

    def advanced_values(self):
        t = [tokens.token_value_s(token) for token in self.produced_tokens]
        return " ".join(t)

    def current_block(self):
        return plist.head(self.blocks)

    def next_block(self):
        return plist.head(plist.tail(self.blocks))

    def pop_block(self):
        print "---- POP BLOCK", self.current_block()
        print self.advanced_values()
        self.blocks = plist.tail(self.blocks)
        return self.current_block()

    def _find_level(self):
        token = self._skip_newlines()
        return tokens.token_level(token)

    def _add_block(self, node, type, level_tokens=None, terminators=None):
        token = nodes.node_token(node)
        cur = self.current_block()
        level = tokens.token_level(token)
        block = Block(cur.level, level, type, level_tokens, terminators)


        print "---- ADD BLOCK", block
        self.blocks = plist.cons(block, self.blocks)

    def add_child_code_block(self, node):
        # # support for f x y | x y -> 1 | x y -> 3
        # if self.current_block().type == CHILD:
        #     self.pop_block()

        # if self.current_block().is_child():
        #     print self.blocks
        # assert not self.current_block().is_child()
        self._add_block(node, CHILD)

    def add_offside_block(self, node):
        self._add_block(node, OFFSIDE)

    def add_node_block(self, node, level_tokens=None):
        self._add_block(node, NODE, level_tokens=level_tokens)

    def add_free_code_block(self, node, terminators):
        # TODO blocks in operators
        self._skip_newlines()
        self._add_block(node, FREE, terminators=terminators)

    def has_blocks(self):
        return not plist.is_empty(self.blocks)

    def count_blocks(self):
        return plist.length(self.blocks)

    def has_tokens(self):
        return len(self.tokens) > 0

    def has_logic_tokens(self):
        return not self.logical_tokens.is_empty()

    def add_logical_token(self, token):
        print "=*=* ADD LOGICAL", token
        self.logical_tokens.append(token)

    def next_logical(self):
        token = self.logical_tokens.pop()
        # print "=*=* NEXT LOGICAL TOKEN", tokens.token_to_s(token)
        return self.attach_token(token)

    def next_physical(self):
        token = self.tokens[self.index]
        # print "++++ NEXT STREAM TOKEN", tokens.token_to_s(token)
        self.index += 1
        return token

    def _skip_newlines(self):
        token = self.next_physical()
        while tokens.token_type(token) == tt.TT_NEWLINE:
            print "++++ SKIP"
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
        token = self._skip_newlines()
        ttype = tokens.token_type(token)
        cur_type = self.current_type()

        block = self.current_block()
        level = tokens.token_level(token)
        print "----NEW LINE", level, block, tokens.token_to_s(token)

        if cur_type in SKIP_NEWLINE_TOKENS:
            if level <= block.level:
                return indentation_error(u"Indentation level of token next to"
                                         u" operator must be bigger then of parent block",
                                         token)

            return self.next_token()

        if block.is_free() is True:
            if block.has_terminator(ttype):
                self.pop_block()
                # IF TOKEN IS TERMINATOR WE STILL NEED TO PROCEED NEWLINE
                block = self.current_block()
            else:
                return self.next_token()

        if level > block.level:
            self.add_logical_token(tokens.create_indent_token(token))
            return self.next_token()
        else:
            # last_block_level = -2
            blocks = self.blocks
            while True:
                block = plist.head(blocks)
                blocks = plist.tail(blocks)
                if space.isvoid(block):
                    return indentation_error(u"Indentation does not match with any of previous levels", token)

                # if last_block_level == block.level:
                #     print "---- POP SAME LEVEL BLOCK", block, level, block.level
                #     self.blocks = blocks
                #     return self.next()
                #     # continue

                # last_block_level = block.level

                if block.level < level:
                    return indentation_error(u"Invalid indentation level", token)
                elif block.level > level:
                    self.on_dedent(block, token)
                elif block.level == level:
                    if block.push_end_of_expression_on_new_line is True:
                        self.add_logical_token(tokens.create_end_expression_token(token))
                    elif block.is_node():
                        if ttype == tt.TT_END:
                            self.index += 1
                            self.add_logical_token(tokens.create_end_token(token))
                            self.pop_block()
                            # if self.current_physical_type() == tt.TT_NEWLINE:
                            # self.add_logical_token(tokens.create_end_expression_token(token))
                            # self._skip_newlines()

                        elif not block.has_level(ttype):
                            self.add_logical_token(tokens.create_end_token(token))
                            self.add_logical_token(tokens.create_end_expression_token(token))
                            self.pop_block()
                    return self.next_token()

                print "---- POP_BLOCK", block
                print self.advanced_values()
                self.blocks = blocks

    def on_dedent(self, block, token):
        if block.push_end_of_expression_on_new_line is True:
            self.add_logical_token(tokens.create_end_expression_token(token))
        if block.push_end_on_dedent is True:
            self.add_logical_token(tokens.create_end_token(token))
            # if block.push_end_of_expression_on_dedent is True:
            #     self.add_logical_token(tokens.create_end_expression_token(token))

    def attach_token(self, token):
        print "^^^^^ATTACH", tokens.token_to_s(token)
        self.token = token
        self.node = nodes.node_blank(self.token)
        self.produced_tokens.append(self.token)
        return self.node

    def _on_end_token(self, token):
        blocks = self.blocks
        popped = []
        while True:
            block = plist.head(blocks)
            blocks = plist.tail(blocks)
            if block.is_node():
                print "---- POP NODE BLOCK ON END TOKEN"
                print "POPPED BLOCKS", popped
                print self.advanced_values()
                break
            elif block.is_module():
                indentation_error(u"Invalid end keyword", token)
            else:
                popped.append(block)
        self.blocks = blocks

    def next_token(self):
        if self.has_logic_tokens():
            return self.next_logical()

        if self.index >= self.length:
            return self.node

        token = self.next_physical()
        ttype = tokens.token_type(token)

        if ttype == tt.TT_NEWLINE:
            return self._on_newline()

        elif ttype == tt.TT_END:
            self._on_end_token(token)
        elif ttype == tt.TT_ENDSTREAM:
            if not self.current_block().is_module():
                indentation_error(u"Not all blocks closed", token)

        block = self.current_block()

        if block.is_free() and block.has_terminator(ttype):
            self.pop_block()

        return self.attach_token(token)
