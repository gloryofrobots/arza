__author__ = 'gloryofrobots'
from matrix import *

def next_node(m):
    if not len(m):
        return None, None

    col = m[0]
    i = None
    node = None
    for i in range(column_length(col)):
        node = column_at(col, i)
        if node is not None:
            break

    return col, node, i


def split_matrix(m, index):
    spec = []
    deflt = []

    for i in range(1, len(m)):
        col = m[i]
        val = col.get_specialized(index)
        spec.append(val)

    for col in m:
        els = col.get_default(index)
        deflt.append(els)

    return spec, deflt




def generate_node(col, node, pmtext, actions):
    val = column_value(col)
    if is_list_column(col):
        pmtext.add_term("if(islist(X))")
        pmtext.add_term("v")


def generate(col, node, spec):
    t = PMText()
    actions = []
    if is_list_column(col):
        t.add_term("if(islist(X))")
        for spec_col in spec:
            pattern = spec_col[0]
            if is_constant_pattern(pattern):
                t.add_term("if(islist(X))")
    pass

def _compile(m, res):
    print "........................................................"
    score_matrix(m)
    m = sort_matrix(m)
    print "________________________SORTED____________________________"
    print_matrix(m)

    col, node, y = next_node(m)
    if node is None:
        return

    assert y is not None
    spec, deflt = split_matrix(m, y)
    print "________________________NODE____________________________"
    print node
    print "________________________SPEC____________________________*"
    print_matrix(spec)
    print "______________________DEFLT____________________________*"
    print_matrix(deflt)
    generate(node, spec, res)
    _compile(deflt, res)

def compile_matrix(m):
    result = []
    _compile(m, result)

PATTERNS = [
    value_pattern(1),
    list_pattern([value_pattern(1), value_pattern(2), value_pattern(3)]),
    table_pattern({"a": value_pattern(1), "b": value_pattern(2), "c": wildcard_pattern()}),
    list_pattern([value_pattern(2), value_pattern(4)]),
    list_pattern([value_pattern(5), value_pattern(6), value_pattern(7), value_pattern(8)]),
    constant_pattern(True),
    wildcard_pattern()
]

PATTERNS = [
    list_pattern([value_pattern(1), value_pattern(2), value_pattern(3)]),
    list_pattern([value_pattern(5), value_pattern(6), value_pattern(7), value_pattern(8)]),
]

m = create_matrix(PATTERNS)
print_matrix(m)

# m = sort_matrix(m)
# print
# print "******************************************"
# print
# print_matrix(m)
compile_matrix(m)
