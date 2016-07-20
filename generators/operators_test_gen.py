# from __future__ import division
import random
from itertools import chain, izip
import math


def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)


def interleave(list_a, list_b):
    return list(chain.from_iterable(izip(list_a, list_b)))

def integers(min, max, count):
    return [random.randint(min, max) for _ in range(count)]

def floats(min, max, count):
    return [random.uniform(min, max) for _ in range(count)]

def flatten(lst):
    return list(chain.from_iterable(lst))

NUM_TEST = 4

ARITH_TESTS = flatten([
   integers(0, 10, NUM_TEST),
   integers(10, 100, NUM_TEST) ,
   integers(100, 1000, NUM_TEST) ,
   integers(1000, 10000, NUM_TEST) ,

   integers(-10, 0, NUM_TEST) ,
   integers(-100, -10, NUM_TEST) ,
   integers(-1000, -100, NUM_TEST) ,
   integers(-10000, -1000, NUM_TEST) ,

   interleave(integers(-100, 0,  NUM_TEST), integers(0, 100,  NUM_TEST)),
   interleave(integers(-1000, -900,  NUM_TEST), integers(900, 1000,  NUM_TEST)),

   floats(0, 10, NUM_TEST),
   floats(10, 100, NUM_TEST) ,
   floats(100, 1000, NUM_TEST) ,
   floats(1000, 10000, NUM_TEST) ,

   floats(-10, 0, NUM_TEST) ,
   floats(-100, -10, NUM_TEST) ,
   floats(-1000, -100, NUM_TEST) ,
   floats(-10000, -1000, NUM_TEST) ,

   interleave(floats(-100, 0,  NUM_TEST), integers(0, 100,  NUM_TEST)),
   interleave(floats(-1000, -900,  NUM_TEST), integers(900, 1000,  NUM_TEST)),
   interleave(floats(-10000, -9000,  NUM_TEST), integers(9000, 10000,  NUM_TEST)),

   interleave(floats(-100, 0,  NUM_TEST), floats(0, 100,  NUM_TEST)),
   interleave(floats(-1000, -900,  NUM_TEST), floats(900, 1000,  NUM_TEST)),
])

BIT_SHIFT_TESTS = flatten([
   interleave(integers(-100, 0,  NUM_TEST), integers(0, 10,  NUM_TEST)),
   interleave(integers(-1000, -900,  NUM_TEST), integers(10, 20,  NUM_TEST)),
   interleave(integers(-10000, -9000,  NUM_TEST), integers(20, 30,  NUM_TEST)),
   interleave(integers(0, 10,  NUM_TEST), integers(0, 100,  NUM_TEST)),
   interleave(integers(10, 100,  NUM_TEST), integers(0, 10,  NUM_TEST)),
   interleave(integers(100, 1000,  NUM_TEST), integers(0, 10,  NUM_TEST)),
   interleave(integers(1000, 10000,  NUM_TEST), integers(0, 100,  NUM_TEST)),
   interleave(integers(-1000, -900,  NUM_TEST), integers(40, 50,  NUM_TEST)),
   interleave(integers(-10000, -9000,  NUM_TEST), integers(0, 50,  NUM_TEST)),

])

BIT_TESTS = flatten([
   interleave(integers(-10000, -9000,  NUM_TEST), integers(9000, 10000,  NUM_TEST)),
   interleave(integers(-10, 10,  NUM_TEST), integers(9000, 10000,  NUM_TEST)),
   interleave(integers(-10000, -9000,  NUM_TEST), integers(-10, 10,  NUM_TEST)),
   interleave(integers(-10, 10,  NUM_TEST), integers(0, 2,  NUM_TEST)),
    ])

def format_result(test, evalstring=None):
    if not evalstring:
        evalstring = test
    try:
        value = eval(evalstring)
        if value is True:
            test_result = "True"
        elif value is False:
            test_result = "False"
        else:
            test_result = str(value)
        return "    affirm:is_equal (%s) (%s)" %  (test, test_result)
    except Exception as e:
        print e
        return "    affirm:is_throw fun | () -> %s end ()" % test


def test_binary(py_op, obin_op, data, result):
    for x,y in pairwise(data):
        test_str = "%s %s %s" % (str(x), obin_op, str(y))
        eval_str = "%s %s %s" % (str(x), py_op, str(y))
        result.append(format_result(test_str, eval_str))

def test_call_binary(obin_op, fn, data, result):
    for x,y in pairwise(data):
        test_str = "%s %s %s" % (str(x), obin_op, str(y))
        eval_str = "%s(%s , %s)" % (fn, str(x), str(y))
        result.append(format_result(test_str, eval_str))


def test_unary(py_op, obin_op, data, result):
    for x in data:
        test_str = "%s (%s)" % (obin_op, str(x))
        eval_str = "%s %s" % (py_op, str(x))
        result.append(format_result(test_str, eval_str))


OP_TABLE = {
  "-":"negate",
  "<":"<",
  ">":">",
  ">=":">=",
  "<=":"<=",
  "==":"==",
  "!=":"!=",
  "+":"+",
  "-":"-",
  "%":"%",
  "*":"*",
  "/":"/",
  # "::":"::",
  # "++":"++",
  "<<": "`lshift`",
  ">>": "`rshift`",
  "&": "`bitand`",
  "^": "`bitxor`",
  "~": "bitnot",
  "%": "`mod`",
}

RESULT = []
for op in ['-', '+', '*', '/', '<', '>', '==', '>=', '<=']:
    test_binary(op, OP_TABLE[op], ARITH_TESTS, RESULT)

test_call_binary(OP_TABLE['%'], 'math.fmod', ARITH_TESTS, RESULT)

for op in ['>>', '<<', '&', '^']:
    test_binary(op, OP_TABLE[op], BIT_SHIFT_TESTS, RESULT)

test_unary('~', OP_TABLE["~"], BIT_SHIFT_TESTS, RESULT)



F = open("test_operators.obn", "w")
T =\
"""
fun test() ->
%s

"""
BODY = "\n".join(RESULT)
F.write(T % BODY)
F.close()
# print BODY

print len(RESULT)
# for t in RESULT:
#      print t
