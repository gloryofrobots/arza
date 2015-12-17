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
    assert True
dis.dis(f)

