
/************************* BASE **********************************/

OAny otostring(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __tostring__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__tostring__ protocol not supported", self);
    }

    return method(S, self);
}

OAny otobool(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __tobool__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__tobool__ protocol not supported", self);
    }

    return method(S, self);
}

OAny oclone(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __clone__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__clone__ protocol not supported", self);
    }

    return method(S, self);
}

OAny ocompare(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __compare__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__compare__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny ohash(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __hash__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__hash__ protocol not supported", self);
    }

    return method(S, self);
}

/************************* COLLECTION **********************************/

OAny oiterator(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __iterator__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__iterator__ protocol not supported", self);
    }

    return method(S, self);
}

OAny olength(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __length__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__length__ protocol not supported", self);
    }

    return method(S, self);
}

OAny ogetitem(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __getitem__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__getitem__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny ohasitem(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __hasitem__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__hasitem__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny odelitem(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __delitem__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__delitem__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny osetitem(OState* S, OAny self, OAny arg1, OAny arg2) {
    ofunc_3 method;
    method = _method(S, self, __setitem__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__setitem__ protocol not supported", self);
    }

    return method(S, self, arg1, arg2);
}

/************************* GENERATOR **********************************/

OAny onext(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __next__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__next__ protocol not supported", self);
    }

    return method(S, self);
}

/************************* NUMBER **********************************/

OAny otointeger(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __tointeger__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__tointeger__ protocol not supported", self);
    }

    return method(S, self);
}

OAny otofloat(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __tofloat__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__tofloat__ protocol not supported", self);
    }

    return method(S, self);
}

OAny otonegative(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __tonegative__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__tonegative__ protocol not supported", self);
    }

    return method(S, self);
}

OAny oinvert(OState* S, OAny self) {
    ofunc_1 method;
    method = _method(S, self, __invert__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__invert__ protocol not supported", self);
    }

    return method(S, self);
}

OAny oadd(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __add__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__add__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny osubtract(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __subtract__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__subtract__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny odivide(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __divide__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__divide__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny omultiply(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __multiply__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__multiply__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny oleftshift(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __leftshift__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__leftshift__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny orightshift(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __rightshift__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__rightshift__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny omod(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __mod__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__mod__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny obitand(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __bitand__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__bitand__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny obitor(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __bitor__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__bitor__ protocol not supported", self);
    }

    return method(S, self, arg1);
}

OAny obitxor(OState* S, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(S, self, __bitxor__);

    if (!method) {
        oraise(S, oerrors(S)->TypeError,
                "__bitxor__ protocol not supported", self);
    }

    return method(S, self, arg1);
}
