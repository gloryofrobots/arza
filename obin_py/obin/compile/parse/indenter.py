from obin.compile.parse import token_type as tt
from obin.compile.parse import nodes
from obin.compile.parse import tokens
from obin.types import api, space, plist, root


class Fifo:
    def __init__(self):
        self.first = ()

    def is_empty(self):
        v = self.first == ()
        return v

    def append(self, data):
        node = [data, ()]
        if self.first:
            self.last[1] = node
        else:
            self.first = node
        self.last = node

    def pop(self):
        node = self.first
        self.first = node[1]
        return node[0]


class InvalidIndentationError(Exception):
    def __init__(self, msg, position, line, column):
        self.position = position
        self.line = line
        self.column = column
        self.msg = msg

    def __str__(self):
        return self.msg


MODULE = -1
CODE = 0
PARENT = 1
CHILD = 2
FREE = 3


class Block(root.W_Root):
    def __init__(self, parent_level, level, type):
        self.parent_level = parent_level
        self.level = level
        self.type = type

    def block_type_to_string(self):
        bt = self.type
        if bt == CODE:
            return "CODE"
        elif bt == PARENT:
            return "PARENT"
        elif bt == CHILD:
            return "CHILD"
        elif bt == FREE:
            return "FREE"
        elif bt == MODULE:
            return "MODULE"

    @property
    def push_end_of_expression_on_new_line(self):
        return self.type == CHILD or self.type == CODE

    @property
    def push_end_on_dedent(self):
        return self.type == CODE or self.type == PARENT

    def _to_string_(self):
        return "<Block pl=%d, l=%d, t=%s>" % (self.parent_level, self.level, self.block_type_to_string())

    def is_code(self):
        return self.type == CODE

    def is_parent(self):
        return self.type == PARENT

    def is_child(self):
        return self.type == CHILD

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

        # first = self.tokens[0]
        # if api.to_i(tokens.token_column(first)) != 1:
        #     indentation_error(u"First line indented", first)
        # self.attach_token(self.tokens[0])
        level = self._find_level()
        self.blocks = plist.plist([Block(-1, level, MODULE)])

    def current_block(self):
        return plist.head(self.blocks)

    def pop_block(self):
        print "---- POP_BLOCK", self.current_block()
        self.blocks = plist.tail(self.blocks)

    def _find_level(self):
        token = self._skip_newlines()
        return tokens.token_level(token)

    def __add_block(self, block):
        print "---- ADD BLOCK", block
        self.blocks = plist.cons(block, self.blocks)

    def _add_block_for_next_token(self, type):
        cur = self.current_block()
        level = self._find_level()
        block = Block(cur.level, level, type)
        self.__add_block(block)

    def _add_block_for_node_token(self, node, type):
        token = nodes.node_token(node)
        cur = self.current_block()
        level = tokens.token_level(token)
        block = Block(cur.level, level, type)
        self.__add_block(block)

    def _add_block_for_current_token(self, type):
        cur = self.current_block()
        level = tokens.token_level(self.token)
        block = Block(cur.level, level, type)
        self.__add_block(block)

    def add_child_code_block(self):
        # # support for f x y | x y -> 1 | x y -> 3
        # if self.current_block().type == CHILD:
        #     self.pop_block()

        assert not self.current_block().is_child()
        self._add_block_for_next_token(CHILD)

    def add_code_block(self):
        self._add_block_for_next_token(CODE)

    def add_parent_code_block(self, node=None):
        if node is None:
            self._add_block_for_current_token(PARENT)
        else:
            self._add_block_for_node_token(node, PARENT)

    def add_free_code_block(self):
        self._add_block_for_current_token(FREE)

    def set_current_block_as_parent(self):
        type = self.current_block().type
        print "---- SET PARENT", self.current_block()
        self.current_block().type = PARENT
        return type

    def set_current_block_type(self, type):
        print "---- SET TYPE", type, self.current_block()
        self.current_block().type = type

    def has_blocks(self):
        return not plist.is_empty(self.blocks)

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

    def _on_indentation(self):
        token = self._skip_newlines()
        level = tokens.token_level(token)

        block = self.current_block()

        # new free block
        if block.is_free() is True:
            # if level <= block.parent_level:
            #     return indentation_error(u"Indentation level of free block must be lesser then of parent block",
            #                              token)
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
                print "---- POP_BLOCK", block
                self.blocks = blocks

    def on_newline(self, block, token):
        if block.push_end_of_expression_on_new_line is True:
            self.add_logical_token(tokens.create_end_expression_token(token))

    def on_dedent(self, block, token):
        if block.push_end_of_expression_on_new_line is True:
            self.add_logical_token(tokens.create_end_expression_token(token))
        if block.push_end_on_dedent is True:
            self.add_logical_token(tokens.create_end_token(token))

    def attach_token(self, token):
        print "^^^^^ATTACH", tokens.token_to_s(token)
        self.token = token
        self.node = nodes.node_blank(self.token)
        return self.node

    def next(self):
        if self.has_logic_tokens():
            return self.next_logical()

        if self.index >= self.length:
            return self.node

        token = self.next_physical()
        ttype = tokens.token_type(token)
        if ttype == tt.TT_NEWLINE:
            return self._on_indentation()

        elif ttype == tt.TT_END:
            block = self.current_block()
            if block.is_child():
                self.pop_block()
                self.pop_block()
            else:
                self.pop_block()

            if not self.has_blocks():
                indentation_error(u"End keyword without an block", token)

        return self.attach_token(token)
