

def not_w(process, val):
    v = api.to_b(val)
    return space.newbool(not v)


def eq_w(process, op1, op2):
    return api.equal(op1, op2)

def in_w(process, left, right):
    return api.contains(right, left)


def notin_w(process, left, right):
    return space.newbool(not api.contains_b(right, left))


def noteq_w(process, op1, op2):
    # TODO api.ne
    return space.newbool(not api.to_b(api.equal(op1, op2)))


def isnot_w_w(process, op1, op2):
    # TODO api.isnot
    return space.newbool(not api.to_b(api.strict_equal(op1, op2)))


def is_w_w(process, op1, op2):
    return api.strict_equal(op1, op2)

