"""
-- It represents a simple ordered couple in the form (key, value)
data Element a b = Element (a, b)
    deriving (Show)

-- It represents a (unordered) list of elements in the form (key, value)
data Dictionary a b = Dictionary [Element a b]
    deriving (Show)

-- It represents a simple dictionary which will be used for my tests
t :: Dictionary String Int
t = Dictionary [Element ("ASD", 1), Element ("FGH", 2)]

couples :: Dictionary a b -> [(a, b)]
couples (Dictionary t) = [(k , v) | (Element (k, v)) <- t]

keys:: Dictionary a b -> [a]
keys (Dictionary t) = [k | (Element (k, v)) <- t]

main :: IO()
main = print (keys t)"
"""

from hask import *


# @sig(H/ "a" >> "a")
# def iden(x):
#     return x + 100
#
# print iden(1)
#
#
# @sig(H/ "a" >> int >> "a")
# def add(x, y):
#     return x + y
#
# @sig(H/ "a" >> (H/ "a" >> "a") >> "a")
# def apply(x, f):
#     return f(x)
#
# print add(2, 3)
# print apply(2, iden)
#
# Either, Left, Right =\
#     data.Either("a", "b") == d.Left("a") | d.Right("b") & deriving(Read, Show, Eq)
#
# @sig(H/ ("a", str) >> "a")
# def fst(o):
#     return o[0]
#
# class TC(Typeclass):
#     @classmethod
#     def make_instance(typeclass, cls, f):
#         print "---", typeclass
#         type_system.build_instance(TC, cls, {"f":f})
#         return
#
#     @classmethod
#     def derive_instance(typeclass, cls):
#         TC.make_instance(cls, f=lambda x: x)
#         return
#     pass
#
# instance(TC, int).where(f=lambda x: x + 1)
#
#
# @sig(H/ "a" >> "a")
# def f(obj):
#     print "OBJ", obj
#     return TC[obj].f(obj)
#
# # print f1(2)
# print f(1)
#
# # print add(2, 3.0)
#
# # print fst(("c", "c"))
@generic("c")
@sig(H/ "b" >> "c" >> "d")
def plus(x, y):
    pass

@plus.register(int)
@sig(H/ float >> int >> float)
def plus_i(x, y):
    return x + y

@plus.register(float)
@sig(H/ str >> float >> str)
def plus_s(x, y):
    return x + str(y)

# print plus(1.0, 2)
print plus("1.0", 2.0)



