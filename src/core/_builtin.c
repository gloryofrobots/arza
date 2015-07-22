#include <obin.h>

#define _cell_behavior(any) (obin_any_cell(any)->behavior)

#define _behavior_method(traits, method) (traits->method)
#define _behavior(state, any) (obin_any_is_cell(any) ? _cell_behavior(any) : _embedded_type_behavior(state, any))

#define _method(state, any, method) (_behavior_method(_behavior(state, any), method))


ObinAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
ObinAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
ObinAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
ObinAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

ObinAny obin_any_new() {
	ObinAny proto;
	proto.type = EOBIN_TYPE_UNKNOWN;
	return proto;
}

/******************************************************************/

static ObinBehavior*
_embedded_type_behavior(ObinState* state, ObinAny any) {
	switch (any.type) {
	case EOBIN_TYPE_TRUE:
	case EOBIN_TYPE_FALSE:
		return obin_bool_behavior();
		break;
	case EOBIN_TYPE_INTEGER:
		return obin_integer_behavior();
		break;
	case EOBIN_TYPE_FLOAT:
		return obin_float_behavior();
		break;
	case EOBIN_TYPE_CHAR:
		return obin_char_behavior();
		break;
	default:
		obin_raise(state, obin_errors(state)->TypeError,
				"There are no native behavior in this type", any);
		return NULL;
	}
}

/*Returns iterator if can, else raise InvalidArgumentError*/
ObinAny obin_iterator(ObinState * state, ObinAny any) {
	obin_func_1 method;
	method = _method(state, any, __iterator__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__iterator__ protocol not supported", any);
	}

	return method(state, any);
}

/*Returns next value from iterator, Nothing if end*/
ObinAny obin_next(ObinState * state, ObinAny any) {
	obin_func_1 method;

	method = _method(state, any, __next__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__next__ protocol not supported", any);
	}

	return method(state, any);
}

void obin_release(ObinState * state, ObinAny self) {
	/*TODO IMPLEMENT*/
}

ObinAny obin_equal(ObinState * state, ObinAny any, ObinAny other) {
	ObinAny result;
	result = obin_compare(state, any, other);
	return obin_is(state, result, obin_integers(state)->Equal);
}

ObinAny obin_compare(ObinState * state, ObinAny any, ObinAny other) {
	obin_func_2 method;

	method = _method(state, any, __compare__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__compare__ protocol not supported", any);
	}

	return method(state, any, other);
}

ObinAny obin_is(ObinState * state, ObinAny any, ObinAny other) {
	if (obin_any_is_cell(any)) {
		if (obin_any_is_cell(other)) {
			return obin_bool_new(obin_any_cell(any) == obin_any_cell(other));
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
		return obin_bool_new(obin_any_integer(any) == obin_any_integer(other));
	case EOBIN_TYPE_CHAR:
		return obin_bool_new(obin_any_char(any) == obin_any_char(other));
	default:
		/*Other things are definitely not the same including floats*/
		return ObinFalse;
	}
}

ObinAny obin_hash(ObinState* state, ObinAny any) {
	obin_func_1 method;

	method = _method(state, any, __hash__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__hash__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_clone(ObinState * state, ObinAny any){
	obin_func_1 method;

	method = _method(state, any, __clone__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__clone__ protocol not supported", any);
	}

	return method(state, any);
}


ObinAny obin_tobool(ObinState* state, ObinAny any) {
	obin_func_1 method;

	method = _method(state, any, __tobool__);
	if (!method) {

		obin_raise(state, obin_errors(state)->TypeError,
				"__tobool__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_tostring(ObinState* state, ObinAny any) {
	obin_func_1 method;

	method = _method(state, any, __tostring__);
	if (!method) {
		if(_behavior(state, any)) {
			return obin_string_new(state, _behavior(state, any)->__name__);
		} else {
			obin_raise(state, obin_errors(state)->TypeError,
				"__tostring__ protocol not supported", any);
		}
	}

	return method(state, any);
}

ObinAny obin_length(ObinState* state, ObinAny any){
	obin_func_1 method;

	method = _method(state, any, __length__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__length__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_getitem(ObinState* state, ObinAny any, ObinAny key){
	obin_func_2 method;

	method = _method(state, any, __getitem__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__getitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_hasitem(ObinState* state, ObinAny any, ObinAny key){
	obin_func_2 method;

	method = _method(state, any, __hasitem__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__hasitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_delitem(ObinState* state, ObinAny any, ObinAny key){
	obin_func_2 method;

	method = _method(state, any, __delitem__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__delitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_add(ObinState* state, ObinAny first, ObinAny second) {
	obin_func_2 method;

	method = _method(state, first, __add__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__add__ protocol not supported", first);
	}

	return method(state, first, second);

}

ObinAny obin_setitem(ObinState* state, ObinAny any, ObinAny key, ObinAny value){
	obin_func_3 method;

	method = _method(state, any, __setitem__);
	if (!method) {
		obin_raise(state, obin_errors(state)->TypeError,
				"__setitem__ protocol not supported", any);
	}

	return method(state, any, key, value);
}
