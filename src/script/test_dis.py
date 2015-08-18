


import dis

class X(object):
    SOME_VAR = 1
    def __init__(self, x, y):
        super(self, X).__init__()
        self.x = x
        self.y = y

    def __add__(self, other):
        class Y(X):
            pass
        return X(self.x+other.x, self.y+other.y)

    def action(self):
        print "Action"
#dis.dis(X)




Env = {}

TXT = """
def func():
    print 1
"""

exec("12+24", globals(), Env)
#print Env

GV = 1

def main():
    GV = 2
    print GV
print GV
main()