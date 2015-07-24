
/************************* BASE **********************************/

ObinAny obin_tostring(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __tostring__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tostring__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_tobool(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __tobool__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tobool__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_clone(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __clone__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__clone__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_compare(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __compare__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__compare__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_hash(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __hash__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hash__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* COLLECTION **********************************/

ObinAny obin_iterator(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __iterator__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__iterator__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_length(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __length__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__length__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_getitem(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __getitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__getitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_hasitem(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __hasitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hasitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_delitem(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __delitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__delitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_setitem(ObinState* state, ObinAny self, ObinAny arg1, ObinAny arg2) {
    obin_func_3 method;
    method = _method(state, self, __setitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__setitem__ protocol not supported", self);
    }

    return method(state, self, arg1, arg2);
}

/************************* GENERATOR **********************************/

ObinAny obin_next(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __next__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__next__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_CAST **********************************/

ObinAny obin_tointeger(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __tointeger__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tointeger__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_tofloat(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __tofloat__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tofloat__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_topositive(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __topositive__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__topositive__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_tonegative(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __tonegative__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tonegative__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_OPERATIONS **********************************/

ObinAny obin_abs(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __abs__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__abs__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_invert(ObinState* state, ObinAny self) {
    obin_func_1 method;
    method = _method(state, self, __invert__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__invert__ protocol not supported", self);
    }

    return method(state, self);
}

ObinAny obin_add(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __add__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__add__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_subtract(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __subtract__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__subtract__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_divide(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __divide__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__divide__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_multiply(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __multiply__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__multiply__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_pow(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __pow__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__pow__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_leftshift(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __leftshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__leftshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_rightshift(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __rightshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__rightshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_mod(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __mod__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__mod__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_and(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __and__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__and__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_or(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __or__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__or__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

ObinAny obin_xor(ObinState* state, ObinAny self, ObinAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __xor__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__xor__ protocol not supported", self);
    }

    return method(state, self, arg1);
}
