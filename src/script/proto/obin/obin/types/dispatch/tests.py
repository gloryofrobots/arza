from obin.types import api

def make_method(process, name, arity=3):
    from obin.types.space import newtrait, newgeneric,  newnativefunc, newtuple, newsymbol
    return newnativefunc(newsymbol(process, unicode(name)), lambda *args: name, arity)

def specify(generic, sig, name):
    arity = api.n_length(sig)
    method = make_method(name, arity)
    generic.specify_single(sig, method)

def sig(*args):
    from obin.types.space import newtuple
    return newtuple(list(args))

def makeobject(traits):
    from obin.types.space import newplainobject, newtuple
    from obin.types import oobject
    o = newplainobject()
    oobject.set_traits(o, newtuple(traits))
    return o


def objects(traits_list):
    from obin.types.space import newtuple
    return newtuple([makeobject(traits) for traits in traits_list])

def test(gen, expected, args):
    m = gen.lookup_method(args)
    res = m._function_(*(args.to_py_list()))
    if res != expected:
        print "ERROR", res, expected
        raise RuntimeError((res, expected))

def test_3():
    from obin.types.space import newtrait, newgeneric
    X = newtrait(newsymbol(u"X"))
    Y = newtrait(newsymbol(u"Y"))
    Z = newtrait(newsymbol(u"Z"))
    g = newgeneric(newsymbol(u"TEST_3"))
    g.specify_single(sig(X, Y, Z), make_method("m1"))
    g.specify_single(sig(X, Z, Z), make_method("m6"))
    g.specify_single(sig(Y, Y, Z), make_method("m2"))
    g.specify_single(sig(Z, Z, Z), make_method("m3"))
    g.specify_single(sig(Z, Z, X), make_method("m4"))
    g.specify_single(sig(Y, Y, X), make_method("m5"))
    g.specify_single(sig(Y, X, X), make_method("m7"))
    test(g, "m1", objects([[X,X], [X,Y], [Y,Y,Z]]))
    test(g, "m2", objects([[Y,Y], [X,Y], [Y,Y,Z]]))
    g.specify_single(sig(X, X, Y), make_method("m8"))
    g.specify_single(sig(X, X, X), make_method("m7"))
    test(g, "m8", objects([[X,X], [X,Y], [Y,Y,Z]]))
    test(g, "m1", objects([[X,X], [Y,X], [Y,Y,Z]]))

def test_any():
    from obin.types.space import newtrait, newgeneric, newsymbol,\
        stdlib, newtuple, newnil, newbool, newint, newprocess
    newprocess(["."])

    Any = stdlib.traits.Any
    Object = stdlib.traits.Object
    Vector = stdlib.traits.Vector
    String = stdlib.traits.String
    X = newtrait(newsymbol(u"X"))
    Y = newtrait(newsymbol(u"Y"))
    Z = newtrait(newsymbol(u"Z"))
    g = newgeneric(newsymbol(u"TEST_ANY"))
    specify(g, sig(String, X, Any, Any), "m1")
    specify(g, sig(String, Any, Any, Any), "m2")
    specify(g, sig(Any, Any, Any, String), "m3")
    specify(g, sig(Any, X, Vector, String), "m4")
    specify(g, sig(Y, X, Any, Z), "m5")
    specify(g, sig(Any, Any, Any, Any), "m6")
    specify(g, sig(Y, X, Z, X), "m7")

    specify(g, sig(Any, Vector, Any), "m8")
    specify(g, sig(Any, Vector, Object), "m9")
    specify(g, sig(Any, Vector, String), "m10")
    specify(g, sig(Any, Vector, String), "m11")

    assert len(g._dags_[4].discriminators) == 12
    assert len(g._dags_[3].discriminators) == 5

    test(g, "m1", newtuple([
        newsymbol(u"S1"),
        makeobject([Y,Z,Z,X]),
        newint(111),
        newbool(True)
    ]))


    test(g, "m2", newtuple([
        newsymbol(u"S1"),
        newint(42),
        newint(111),
        newbool(True)
    ]))

    test(g, "m3", newtuple([
        newnil(),
        newint(42),
        newint(111),
        newsymbol(u"S1")
    ]))

    test(g, "m4", newtuple([
        newnil(),
        makeobject([Z,Z,Y,Z,X]),
        newtuple([newbool(True), newbool(False)]),
        newsymbol(u"S1")
    ]))
    test(g, "m5", newtuple([
        makeobject([Z,Z,Y,Z,X]),
        makeobject([X]),
        newtuple([newbool(True), newbool(False)]),
        makeobject([X,Z]),
    ]))
    test(g, "m6", newtuple([
        newnil(),
        newnil(),
        newnil(),
        newnil(),
    ]))

    test(g, "m7", newtuple([
        makeobject([Z,Z,Y,Z,X]),
        makeobject([X]),
        makeobject([X,Z]),
        makeobject([X,Z]),
    ]))

    test(g, "m8", newtuple([
        newnil(),
        newtuple([newbool(True), newbool(False)]),
        newnil(),
    ]))

    test(g, "m9", newtuple([
        newnil(),
        newtuple([newbool(True), newbool(False)]),
        makeobject([X,Z]),
    ]))

