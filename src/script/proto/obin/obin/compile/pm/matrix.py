__author__ = 'gloryofrobots'
from pattern import *
from column import *

"""

(let [x true
      y true
      z true]
  (match [x y z]
    [_ false true] 1
    [false true _ ] 2
    [_ _ false] 3
    [_ _ true] 4
    :else 5))

x y z
-------
[_ f t] 1
[f t _] 2
[_ _ f] 3
[_ _ t] 4
[_ _ _] 5

"""


def matrix_height(m):
    col = m[0]
    return len(col.patterns)


def print_matrix(m):
    rows = []
    for col in m:
        row = ["%s(%d)" % (str(col.type), col.score)]
        for p in col.patterns:
            row.append(str(p))
        rows.append(row)

    rows = zip(*rows)
    for row in rows:
        print "".join(p.ljust(20) for p in row)


def get_matrix_column(matrix, type, val):
    for col in matrix:
        if column_equal(col, type, val):
            return col
    return None


def add_matrix_column(matrix, type, val):
    col = Column(type(val), None)
    matrix.append(col)


def add_matrix_column_if_not_exist(matrix, type, val):
    col = get_matrix_column(matrix, type, val)
    if col:
        return

    col = Column(type(val), None)
    matrix.append(col)


def create_matrix(patterns):
    matrix = []
    for pattern in patterns:
        if is_list_pattern(pattern):
            type = ListColumnType
            for index in xrange(len(pattern_value(pattern))):
                add_matrix_column_if_not_exist(matrix, type, index)

        elif is_table_pattern(pattern):
            type = TableColumnType
            for key in pattern_value(pattern):
                add_matrix_column_if_not_exist(matrix, type, key)
        else:
            type = VarColumnType
            add_matrix_column_if_not_exist(matrix, type, "X")

    for col in matrix:
        val = column_value(col)
        if is_list_column(col):
            for pattern in patterns:
                if not is_list_pattern(pattern):
                    col.add_pattern(None)
                    continue
                p = pattern_value(pattern)
                if val < len(p):
                    col.add_pattern(p[val])
                else:
                    col.add_pattern(None)
        elif is_table_column(col):
            for pattern in patterns:
                if not is_table_pattern(pattern):
                    col.add_pattern(None)
                    continue
                p = pattern_value(pattern)
                if val in p:
                    col.add_pattern(p[val])
                else:
                    col.add_pattern(None)
        elif is_var_column(col):
            for p in patterns:
                if is_value_pattern(p) or is_wildcard_pattern(p) or is_constant_pattern(p):
                    col.add_pattern(p)
                else:
                    col.add_pattern(None)
        else:
            raise RuntimeError(col)

    return matrix


def score_column(col):
    score = 0
    for p in col.patterns:
        if p is None:
            continue
        elif is_value_pattern(p) or is_constant_pattern(p):
            score += 1
        elif is_wildcard_pattern(p):
            break
    return score


def score_matrix(m):
    for col in m:
        col.score = score_column(col)


def sort_matrix(m):
    m = sorted(m, key=lambda col: col.score, reverse=True)
    return m


