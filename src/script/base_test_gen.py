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
            test_result = "true"
        elif value is False:
            test_result = "false"
        else:
            test_result = str(value)
        return "    testit.assert_equal(%s, %s)" %  (test, test_result)
    except Exception as e:
        print e
        return "    testit.assert_throw(fun -> %s end, ())" % test


def test_binary(op, data, result):
    for x,y in pairwise(data):
        test_str = "%s %s %s" % (str(x), op, str(y))
        result.append(format_result(test_str))

def test_call_binary(op, fn, data, result):
    for x,y in pairwise(data):
        test_str = "%s %s %s" % (str(x), op, str(y))
        eval_str = "%s(%s, %s)" % (fn, str(x), str(y))
        result.append(format_result(test_str, eval_str))


def test_unary(op, data, result):
    for x in data:
        test_str = "%s%s" % (op, str(x))
        result.append(format_result(test_str))

RESULT = []
for op in ['-', '+', '*', '/', '<', '>', '==', '>=', '<=']:
    test_binary(op, ARITH_TESTS, RESULT)

test_call_binary('%', 'math.fmod', ARITH_TESTS, RESULT)

for op in ['>>', '<<', '&',  '|', '^']:
    test_binary(op, BIT_SHIFT_TESTS, RESULT)

test_unary('~', BIT_SHIFT_TESTS, RESULT)



F = open("test_operators.obn", "w")
T =\
"""
def test() ->
%s
end
"""
BODY = "\n".join(RESULT)
F.write(T % BODY)
F.close()
# print BODY

print len(RESULT)
# for t in RESULT:
#      print t