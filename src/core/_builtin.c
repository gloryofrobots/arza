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
_embedded_type_behavior(OState* state, OAny any) {
	switch (any.type) {
	case EOBIN_TYPE_TRUE:
		return obehaviors(state)->True;
	case EOBIN_TYPE_FALSE:
		return obehaviors(state)->False;
	case EOBIN_TYPE_INTEGER:
		return obehaviors(state)->Integer;
	case EOBIN_TYPE_FLOAT:
		return obehaviors(state)->Float;
	case EOBIN_TYPE_CHAR:
		return obehaviors(state)->Char;
	default:
		oraise(state, oerrors(state)->TypeError,
				"There are no native behavior in this type", any);
		return NULL;
	}
}

void orelease(OState * state, OAny self) {
	/*TODO IMPLEMENT*/
}

OAny oequal(OState * state, OAny any, OAny other) {
	OAny result;
	result = ocompare(state, any, other);
	return ois(state, result, ointegers(state)->Equal);
}

OAny ois(OState * state, OAny any, OAny other) {
	if (OAny_isCell(any)) {
		if (OAny_isCell(other)) {
			return OBool(OAny_toCell(any) == OAny_toCell(other));
		}

		return ObinFalse;
	}
	switch (any.type) {
	case EOBIN_TYPE_FALSE:
	case EOBIN_TYPE_TRUE:
	case EOBIN_TYPE_NIL:
	case EOBIN_TYPE_NOTHING:
		return OBool(any.type == other.type);
	case EOBIN_TYPE_INTEGER:
		return OBool(OAny_toInt(any) == OAny_toInt(other));
	case EOBIN_TYPE_CHAR:
		return OBool(OAny_toChar(any) == OAny_toChar(other));
	default:
		/*Other things are definitely not the same including floats*/
		return ObinFalse;
	}
}


/************************* BASE **********************************/

OAny otostring(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tostring__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__tostring__ protocol not supported", self);
    }

    return method(state, self);
}

OAny otobool(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tobool__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__tobool__ protocol not supported", self);
    }

    return method(state, self);
}

OAny oclone(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __clone__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__clone__ protocol not supported", self);
    }

    return method(state, self);
}

OAny ocompare(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __compare__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__compare__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny ohash(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __hash__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__hash__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* COLLECTION **********************************/

OAny oiterator(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __iterator__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__iterator__ protocol not supported", self);
    }

    return method(state, self);
}

OAny olength(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __length__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__length__ protocol not supported", self);
    }

    return method(state, self);
}

OAny ogetitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __getitem__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__getitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny ohasitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __hasitem__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__hasitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny odelitem(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __delitem__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__delitem__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny osetitem(OState* state, OAny self, OAny arg1, OAny arg2) {
    ofunc_3 method;
    method = _method(state, self, __setitem__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__setitem__ protocol not supported", self);
    }

    return method(state, self, arg1, arg2);
}

/************************* GENERATOR **********************************/

OAny onext(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __next__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__next__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_CAST **********************************/

OAny otointeger(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tointeger__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__tointeger__ protocol not supported", self);
    }

    return method(state, self);
}

OAny otofloat(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tofloat__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__tofloat__ protocol not supported", self);
    }

    return method(state, self);
}

OAny otopositive(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __topositive__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__topositive__ protocol not supported", self);
    }

    return method(state, self);
}

OAny otonegative(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __tonegative__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__tonegative__ protocol not supported", self);
    }

    return method(state, self);
}

/************************* NUMBER_OPERATIONS **********************************/

OAny oabs(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __abs__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__abs__ protocol not supported", self);
    }

    return method(state, self);
}

OAny oinvert(OState* state, OAny self) {
    ofunc_1 method;
    method = _method(state, self, __invert__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__invert__ protocol not supported", self);
    }

    return method(state, self);
}

OAny oadd(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __add__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__add__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny osubtract(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __subtract__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__subtract__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny odivide(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __divide__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__divide__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny omultiply(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __multiply__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__multiply__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny opow(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __pow__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__pow__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny oleftshift(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __leftshift__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__leftshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny orightshift(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __rightshift__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__rightshift__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny omod(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __mod__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__mod__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny oand(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __and__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__and__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny oor(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __or__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__or__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

OAny oxor(OState* state, OAny self, OAny arg1) {
    ofunc_2 method;
    method = _method(state, self, __xor__);

    if (!method) {
        oraise(state, oerrors(state)->TypeError,
                "__xor__ protocol not supported", self);
    }

    return method(state, self, arg1);
}

