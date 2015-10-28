import dis

class C(object):
    def __init__(self, x):
        self.x = x

    def action(self, *args):
        print "ARGS", args


def f2(x, y):
    print x + y

def m1(self):
    print self.x


def f(*args):

    o = C(42)
    o.action(1,2, *args)
    f2(1,2)
    d = {"key":"value", "key2":"value"}

f("arg1", "arg2")

dis.dis(f)


