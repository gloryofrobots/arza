#include <core/omemory.h>
#include <core/obuiltin.h>
#include <types/oerror.h>
#include <types/ostring.h>

ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell) {
	ObinAny result;
	obin_assert(obin_type_is_cell(type));

	result = obin_any_new();
	obin_any_init_cell(result, type, cell);
	return result;
}

#define _cell_traits(any) (obin_any_cell(any)->native_traits)

#define _traits_method(traits, method) (traits->method)
#define _traits(state, any) (obin_any_is_cell(any) ? _cell_traits(any) : _embedded_type_traits(state, any))

#define _method(state, any, method) (_traits_method(_traits(state, any), method))

#define _subtrait_method(state, any, traitname, method) \
		(_traits(state, any)->traitname != 0 ? \
			(_traits_method(_traits(state, any)->traitname, method)) \
			: 0 )

#define _collection_method(state, any, method) _subtrait_method(state, any, collection, method)
#define _generator_method(state, any, method) _subtrait_method(state, any, generator, method)
#define _number_method(state, any, method) _subtrait_method(state, any, number, method)

static ObinNativeTraits __EMPTY_TRAITS__ = {
	"undefined",
	 0, /*__tostring__,*/
	 0, /*__destroy__,*/
	 0, /*__clone__,*/
	 0, /*__compare__,*/
	 0, /*__hash__,*/

     0, /*collection*/
	 0, /*iterator*/
	 0 /*number*/
};

static ObinNativeTraits*
_embedded_type_traits(ObinState* state, ObinAny any) {
	switch (any.type) {
	case EOBIN_TYPE_INTEGER:
		return obin_integer_traits();
		break;
	case EOBIN_TYPE_FLOAT:
		return obin_float_traits();
		break;
	case EOBIN_TYPE_BIG_INTEGER:
		return obin_big_integer_traits();
		break;
	default:
		obin_raise_type_error(state, "There are no native traits in this type", any);
		return &__EMPTY_TRAITS__;
	}
}

ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell) {
	ObinAny result;
	obin_assert(obin_type_is_cell(type));

	result = obin_any_new();

	obin_any_init_cell(result, type, cell);

	return result;
}

/*Returns iterator if can, else raise InvalidArgumentError*/
ObinAny obin_iterator(ObinState * state, ObinAny any) {
	obin_method method;
	method = _collection_method(state, any, __iterator__);
	if (!method) {
		return obin_raise_type_error(state, "__iterator__ protocol not supported", any);
	}

	return method(state, any);
}

/*Returns next value from iterator, Nothing if end*/
ObinAny obin_next(ObinState * state, ObinAny any) {
	obin_method method;

	method = _generator_method(state, any, __next__);
	if (!method) {
		return obin_raise_type_error(state, "__next__ protocol not supported", any);
	}

	return method(state, any);
}

/* destroy cell */
ObinAny obin_cell_destroy(ObinState * state, ObinAny any) {
	obin_assert(obin_any_is_cell(any));
	obin_free(obin_any_cell(any));
	return ObinNothing;
}

ObinAny obin_destroy(ObinState * state, ObinAny any) {
	obin_method method;

	if (!obin_any_is_cell(any)) {
		return obin_raise_type_error(state, "Cell expected", any);
	}

	method = _method(state, any, __destroy__);
	if (!method) {
		method = &obin_cell_destroy;
	}

	return method(state, any);
}

ObinAny obin_equal(ObinState * state, ObinAny any, ObinAny other) {
	ObinAny result;
	result = obin_compare(state, any, other);
	return obin_bool_new(obin_any_is_equal(result));
}

ObinAny obin_compare(ObinState * state, ObinAny any, ObinAny other) {
	obin_method_2 method;

	method = _method(state, any, __compare__);
	if (!method) {
		return obin_raise_type_error(state, "__compare__ protocol not supported", any);
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
	obin_method method;

	method = _method(state, any, __hash__);
	if (!method) {
		return obin_raise_type_error(state, "__hash__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_clone(ObinState * state, ObinAny any){
	obin_method method;

	method = _method(state, any, __clone__);
	if (!method) {
		return obin_raise_type_error(state, "__clone__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_tostring(ObinState* state, ObinAny any) {
	obin_method method;

	method = _method(state, any, __tostring__);
	if (!method) {
		return obin_raise_type_error(state, "__tostring__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_length(ObinState* state, ObinAny any){
	obin_method method;

	method = _collection_method(state, any, __length__);
	if (!method) {
		return obin_raise_type_error(state, "__length__ protocol not supported", any);
	}

	return method(state, any);
}

ObinAny obin_getitem(ObinState* state, ObinAny any, ObinAny key){
	obin_method_2 method;

	method = _collection_method(state, any, __getitem__);
	if (!method) {
		return obin_raise_type_error(state, "__getitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_hasitem(ObinState* state, ObinAny any, ObinAny key){
	obin_method_2 method;

	method = _collection_method(state, any, __hasitem__);
	if (!method) {
		return obin_raise_type_error(state, "__hasitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_delitem(ObinState* state, ObinAny any, ObinAny key){
	obin_method_2 method;

	method = _collection_method(state, any, __delitem__);
	if (!method) {
		return obin_raise_type_error(state, "__delitem__ protocol not supported", any);
	}

	return method(state, any, key);
}

ObinAny obin_setitem(ObinState* state, ObinAny any, ObinAny key, ObinAny value){
	obin_method_3 method;

	method = _collection_method(state, any, __setitem__);
	if (!method) {
		return obin_raise_type_error(state, "__setitem__ protocol not supported", any);
	}

	return method(state, any, key, value);
}
