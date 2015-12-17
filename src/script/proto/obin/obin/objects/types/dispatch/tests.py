def make_method(name, arity=3):
    from obin.objects.space import newtrait, newgeneric, newstring, newprimitive, newvector
    return newprimitive(newstring(name), lambda *args: name, arity)

def specify(generic, sig, name):
    arity = sig.length()
    method = make_method(name, arity)
    generic.specify(sig, method)

def sig(*args):
    from obin.objects.space import newtrait, newgeneric, newstring, newprimitive, newvector
    return newvector(list(args))

def makeobject(traits):
    from obin.objects.space import newplainobject, newvector
    o = newplainobject()
    o.set_traits(newvector(traits))
    return o


def objects(traits_list):
    from obin.objects.space import newplainobject, newvector
    return newvector([makeobject(traits) for traits in traits_list])

def test(gen, expected, args):
    # from obin.objects.object_space import newstring
    # assert m._name_ == newstring(expected)
    m = gen.lookup_method(args)
    res = m._function_(*(args.values()))
    if res != expected:
        print "ERROR", res, expected
        raise RuntimeError((res, expected))

def test_3():
    from obin.objects.space import newtrait, newgeneric, newstring, newprimitive, newvector
    X = newtrait(newstring("X"))
    Y = newtrait(newstring("Y"))
    Z = newtrait(newstring("Z"))
    g = newgeneric(newstring("TEST_3"))
    g.specify(sig(X, Y, Z), make_method("m1"))
    g.specify(sig(X, Z, Z), make_method("m6"))
    g.specify(sig(Y, Y, Z), make_method("m2"))
    g.specify(sig(Z, Z, Z), make_method("m3"))
    g.specify(sig(Z, Z, X), make_method("m4"))
    g.specify(sig(Y, Y, X), make_method("m5"))
    g.specify(sig(Y, X, X), make_method("m7"))
    test(g, "m1", objects([[X,X], [X,Y], [Y,Y,Z]]))
    test(g, "m2", objects([[Y,Y], [X,Y], [Y,Y,Z]]))
    g.specify(sig(X, X, Y), make_method("m8"))
    g.specify(sig(X, X, X), make_method("m7"))
    test(g, "m8", objects([[X,X], [X,Y], [Y,Y,Z]]))
    test(g, "m1", objects([[X,X], [Y,X], [Y,Y,Z]]))

def test_any():
    from obin.objects.space import newtrait, newgeneric, newstring,\
        state, newvector, newnull, newbool, newint
    Any = state.traits.Any
    Object = state.traits.Object
    Vector = state.traits.Vector
    String = state.traits.String
    X = newtrait(newstring("X"))
    Y = newtrait(newstring("Y"))
    Z = newtrait(newstring("Z"))
    g = newgeneric(newstring("TEST_ANY"))
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

    test(g, "m1", newvector([
        newstring("S1"),
        makeobject([Y,Z,Z,X]),
        newint(111),
        newbool(True)
    ]))


    test(g, "m2", newvector([
        newstring("S1"),
        newint(42),
        newint(111),
        newbool(True)
    ]))

    test(g, "m3", newvector([
        newnull(),
        newint(42),
        newint(111),
        newstring("S1")
    ]))

    test(g, "m4", newvector([
        newnull(),
        makeobject([Z,Z,Y,Z,X]),
        newvector([newbool(True), newbool(False)]),
        newstring("S1")
    ]))
    test(g, "m5", newvector([
        makeobject([Z,Z,Y,Z,X]),
        makeobject([X]),
        newvector([newbool(True), newbool(False)]),
        makeobject([X,Z]),
    ]))
    test(g, "m6", newvector([
        newnull(),
        newnull(),
        newnull(),
        newnull(),
    ]))

    test(g, "m7", newvector([
        makeobject([Z,Z,Y,Z,X]),
        makeobject([X]),
        makeobject([X,Z]),
        makeobject([X,Z]),
    ]))

    test(g, "m8", newvector([
        newnull(),
        newvector([newbool(True), newbool(False)]),
        newnull(),
    ]))

    test(g, "m9", newvector([
        newnull(),
        newvector([newbool(True), newbool(False)]),
        makeobject([X,Z]),
    ]))

