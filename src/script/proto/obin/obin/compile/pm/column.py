__author__ = 'gloryofrobots'
class ColumnType(object):
    pass


class ListColumnType(ColumnType):
    def __init__(self, index):
        self.val = index

    def __str__(self):
        return "l_%s" % str(self.val)


class TableColumnType(ColumnType):
    def __init__(self, key):
        self.val = key

    def __str__(self):
        return "t_%s" % str(self.val)


class VarColumnType(ColumnType):
    def __init__(self, name):
        self.val = name

    def __str__(self):
        return "v_%s" % str(self.val)


def is_list_column(col):
    return isinstance(col.type, ListColumnType)


def is_table_column(col):
    return isinstance(col.type, TableColumnType)


def is_var_column(col):
    return isinstance(col.type, VarColumnType)


def column_equal(col, col_type, val):
    if not isinstance(col.type, col_type):
        return False

    return col.type.val == val

def column_at(col, index):
    return col.patterns[index]

def column_value(col):
    return col.type.val

def column_length(col):
    return len(col.patterns)

class Column(object):
    def __init__(self, col_type, patterns):
        if not patterns:
            patterns = []
        self.patterns = patterns
        self.type = col_type
        self.score = 0

    def get_specialized(self, index):
        spec = self.patterns[index]
        return Column(self.type, [spec])

    def get_default(self, index):
        default = self.patterns[0:index] + self.patterns[index+1:]
        return Column(self.type, default)

    def get_pattern(self, i):
        return self.patterns[i]

    def add_pattern(self, p):
        self.patterns.append(p)

    def __repr__(self):
        return "<Col %s %s>" % (str(self.type), str(self.patterns))
