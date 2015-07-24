
/************************* BASE **********************************/

OAny obin_tostring(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tostring__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tostring__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tobool(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tobool__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tobool__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_clone(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __clone__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__clone__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_compare(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __compare__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__compare__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_hash(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __hash__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hash__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* COLLECTION **********************************/

OAny obin_iterator(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __iterator__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__iterator__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_length(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __length__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__length__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_getitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __getitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__getitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_hasitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __hasitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hasitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_delitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __delitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__delitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_setitem(OState* state, OAny self, OAny arg1, OAny arg2) {
    ofunc_3 method;
    method = _method(state, self, __setitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__setitem__ protocol not supported", self);
    }

    return method(state, self, arg1, arg2);
}

/************************* GENERATOR **********************************/

OAny obin_next(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __next__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__next__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tointeger__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tointeger__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tofloat(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tofloat__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tofloat__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_topositive(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __topositive__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__topositive__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tonegative(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tonegative__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tonegative__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __abs__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__abs__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_invert(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __invert__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__invert__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_add(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __add__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__add__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_subtract(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __subtract__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__subtract__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_divide(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __divide__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__divide__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_multiply(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __multiply__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__multiply__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_pow(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __pow__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__pow__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_leftshift(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __leftshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__leftshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_rightshift(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __rightshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__rightshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_mod(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __mod__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__mod__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_and(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __and__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__and__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_or(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __or__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__or__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_xor(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __xor__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__xor__ protocol not supported", self);
    }

    return method(state, self, arg1);
}
