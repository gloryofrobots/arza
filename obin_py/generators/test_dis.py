import dis

class C(object):
    def __init__(self, x):
        self.x = x

    def action(self, *args):
        print "ARGS", args


def f2(x, y):
    print x,y

def m1(self):
    print self.x



def f(*args):
    x, y = f2(1,2) 
    return x, y


dis.dis(f)



def test_transducer():
    l = [1,2,3,4,5]

    def a(x, y):
        return x + y

    def inc(x):
        return x + 1

    r = reduce(a, map(inc, l))
    print r

    # (defn mapping [f]
    #     (fn [f1]
    #       (fn [result input]
    #         (f1 result (f input)))))

    def mapping(f):
        def _w1(f1):
            def _w2(result, inp):
                print "_w2", result, inp
                return f1(result, f(inp))
            return _w2
        return _w1

    # (reduce + 0 (map inc [1 2 3 4]))
    # (reduce ((mapping inc) +) 0 [1 2 3 4])
    r = reduce((mapping(inc))(a), l, 0)
    print r
#test_transducer()