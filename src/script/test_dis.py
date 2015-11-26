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
    for i in range(0, 5):
        10
        20


dis.dis(f)

