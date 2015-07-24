#include <obin.h>

#define _cell_behavior(any) (OAny_toCell(any)->behavior)

#define _behavior_method(traits, method) (traits->method)
#define _behavior(state, any) (OAny_isCell(any) ? _cell_behavior(any) : _embedded_type_behavior(state, any))

#define _method(state, any, method) (_behavior_method(_behavior(state, any), method))

OAny OAny_new() {
	OAny proto;
	proto.type = EOBIN_TYPE_UNKNOWN;
	return proto;
}

/******************************************************************/

static OBehavior*
_embedded_type_behavior(ObinState* state, OAny any) {
	switch (any.type) {
	case EOBIN_TYPE_TRUE:
		return obin_behaviors(state)->True;
	case EOBIN_TYPE_FALSE:
		return obin_behaviors(state)->False;
	case EOBIN_TYPE_INTEGER:
		return obin_behaviors(state)->Integer;
	case EOBIN_TYPE_FLOAT:
		return obin_behaviors(state)->Float;
	case EOBIN_TYPE_CHAR:
		return obin_behaviors(state)->Char;
	default:
		obin_raise(state, obin_errors(state)->TypeError,
				"There are no native behavior in this type", any);
		return NULL;
	}
}

void obin_release(ObinState * state, OAny self) {
	/*TODO IMPLEMENT*/
}

OAny obin_equal(ObinState * state, OAny any, OAny other) {
	OAny result;
	result = obin_compare(state, any, other);
	return obin_is(state, result, obin_integers(state)->Equal);
}

OAny obin_is(ObinState * state, OAny any, OAny other) {
	if (OAny_isCell(any)) {
		if (OAny_isCell(other)) {
			return obin_bool_new(OAny_toCell(any) == OAny_toCell(other));
		}

		return ObinFalse;
	}
	switch (any.type) {
	case EOBIN_TYPE_FALSE:
	case EOBIN_TYPE_TRUE:
	case EOBIN_TYPE_NIL:
	case EOBIN_TYPE_NOTHING:
		return obin_bool_new(any.type == other.type);
	case EOBIN_TYPE_INTEGER:
		return obin_bool_new(OAny_toInt(any) == OAny_toInt(other));
	case EOBIN_TYPE_CHAR:
		return obin_bool_new(OAny_toChar(any) == OAny_toChar(other));
	default:
		/*Other things are definitely not the same including floats*/
		return ObinFalse;
	}
}

/************************* BASE **********************************/

OAny obin_tostring(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __tostring__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tostring__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tobool(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __tobool__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tobool__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_clone(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __clone__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__clone__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_compare(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __compare__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__compare__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_hash(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __hash__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hash__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* COLLECTION **********************************/

OAny obin_iterator(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __iterator__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__iterator__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_length(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __length__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__length__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_getitem(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __getitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__getitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_hasitem(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __hasitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__hasitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_delitem(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __delitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__delitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_setitem(ObinState* state, OAny self, OAny arg1, OAny arg2) {
    obin_func_3 method;
    method = _method(state, self, __setitem__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__setitem__ protocol not supported", self);
    }

    return method(state, self, arg1, arg2);
}

/************************* GENERATOR **********************************/

OAny obin_next(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __next__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__next__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __tointeger__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tointeger__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tofloat(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __tofloat__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tofloat__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_topositive(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __topositive__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__topositive__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_tonegative(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __tonegative__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__tonegative__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __abs__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__abs__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_invert(ObinState* state, OAny self) {
    obin_func_1 method;
    method = _method(state, self, __invert__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__invert__ protocol not supported", self);
    }

    return method(state, self);
}

OAny obin_add(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __add__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__add__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_subtract(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __subtract__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__subtract__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_divide(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __divide__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__divide__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_multiply(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __multiply__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__multiply__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_pow(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __pow__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__pow__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_leftshift(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __leftshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__leftshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_rightshift(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __rightshift__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__rightshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_mod(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __mod__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__mod__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_and(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __and__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__and__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_or(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __or__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__or__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny obin_xor(ObinState* state, OAny self, OAny arg1) {
    obin_func_2 method;
    method = _method(state, self, __xor__);

    if (!method) {
        obin_raise(state, obin_errors(state)->TypeError,
                "__xor__ protocol not supported", self);
    }

    return method(state, self, arg1);
}
