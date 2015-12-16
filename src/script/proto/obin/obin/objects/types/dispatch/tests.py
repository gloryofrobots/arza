def make_method(name):
    from obin.objects.object_space import newtrait, newgeneric, newstring, newprimitive, newvector
    return newprimitive(newstring(name), lambda x, y, z: name, 3)

def sig(*args):
    from obin.objects.object_space import newtrait, newgeneric, newstring, newprimitive, newvector
    return newvector(list(args))

def makeobject(traits):
    from obin.objects.object_space import newplainobject, newvector
    o = newplainobject()
    o.set_traits(newvector(traits))
    return o


def objects(traits_list):
    from obin.objects.object_space import newplainobject, newvector
    return newvector([makeobject(traits) for traits in traits_list])

def test(gen, expected, args):
    m = gen.lookup_method(args)
    res = m._function_(*(args.values()))
    if res != expected:
        print "ERROR", res, expected
        raise RuntimeError((res, expected))

def test_3():
    from obin.objects.object_space import newtrait, newgeneric, newstring, newprimitive, newvector
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
    from obin.objects.object_space import newtrait, newgeneric, newstring, object_space, newvector
    Any = object_space.traits.Any
    Object = object_space.traits.Object
    Vector = object_space.traits.Vector
    String = object_space.traits.String
    X = newtrait(newstring("X"))
    Y = newtrait(newstring("Y"))
    Z = newtrait(newstring("Z"))
    g = newgeneric("TEST_ANY")
    # g.specify(sig(Object, Any, Y, Any), make_method("m1"))
    # g.specify(sig(Any, Vector, Y, X), make_method("m2"))
    # g.specify(sig(Any, Any, Any, Any), make_method("m3"))
    # g.specify(sig(Object, Object, Z, Any), make_method("m4"))
    # g.specify(sig(Vector, Any, Any, Any), make_method("m5"))
    g.specify(sig(String, X, Any, Any), make_method("m5"))
    g.specify(sig(String, Any, Any, Any), make_method("m5"))
    g.specify(sig(Any, Any, Any, Any), make_method("m3"))
    g.specify(sig(Any, Any, Any, String), make_method("m4"))
    g.specify(sig(Any, X, Vector, String), make_method("m4"))
    g.specify(sig(Any, X, Any, Z), make_method("m4"))
    test(g, "m1", newvector(newvector([1,2]), makeobject([X,Y]),
                            [Y,Y,Z]))


