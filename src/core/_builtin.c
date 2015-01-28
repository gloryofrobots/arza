#include "obin.h"

/*Returns true if object is iterable*/
obin_bool obin_any_is_iterable(ObinAny iterable){
	if(!obin_any_is_cell(iterable)){
		return OFALSE;
	}

	if( ((ObinCell*) obin_any_cell(iterable))->type_trait->__iter__ != NULL ) {
		return OTRUE;
	}

	/*HERE check compound cell for iterator*/
	return OFALSE;
}

/*Returns iterator if can, else raise InvalidArgumentError*/
ObinAny obin_iterator(ObinState * state, ObinAny any) {
	ObinAny iterator;
	ObinCell * iterable;

	if(!obin_any_is_iterable(any)){
		obin_raise_invalid_argument(state, "Iterable expected", any);
	}

	iterable = obin_any_cell(any);
	return iterable->type_trait->__iterator__(any);
}

/*Returns next value from iterator, Nothing if end*/
ObinAny obin_next(ObinState * state, ObinAny any){
	obin_function next;

	if(!obin_any_is_cell(any)){
		obin_raise_invalid_argument(state, "Iterator expected", any);
	}

	next = obin_any_cell(any)->type_trait->__next__;
	if(next == 0){
		obin_raise_invalid_argument(state, "Iterator expected, __iter__ not exist", any);
	}

	return next(any);
}

/* destroy cell */
ObinAny obin_destroy(ObinState * state, ObinAny any){
	if(!obin_any_is_cell(any)){
		obin_raise_invalid_argument(state, "Cell expected", any);
	}

	if(!obin_type_has_method(any, __destroy__)) {
		return obin_cell_destroy(state, any);
	}

	return obin_type_call(state, any, __destroy__);
}

ObinAny obin_cell_destroy(ObinState * state, ObinAny any){
	obin_assert(obin_any_is_cell(any));
	obin_free(obin_any_cell(any));
	return ObinNothing;
}


ObinTypeTrait* obin_type_trait(ObinState* state, ObinAny any) {
	if(obin_any_is_cell(any)){
		return any.data.cell->type_trait;
	}

	switch(any.type) {
	case EOBIN_TYPE_INTEGER:
		return obin_integer_type_trait();
		break;
	case EOBIN_TYPE_FLOAT:
		return obin_float_type_trait();
		break;
	case EOBIN_TYPE_BIG_INTEGER:
		return obin_big_integer_type_trait();
		break;
	default:
		return 0;
	}
}

#define CHECK_TRAIT(state, any, method) \
	trait = obin_type_trait(state, any); \
	if(trait == 0 || trait->method == 0) return ObinNothing;

ObinAny obin_equal(ObinState * state, ObinAny any, ObinAny other) {
	ObinTypeTrait* trait;
	CHECK_TRAIT(state, any, __equal__);

	return obin_tt_call_1(__equal__, state, any, other);
}

ObinAny obin_is(ObinState * state, ObinAny any) {

}

ObinAny obin_hash(ObinState* state, ObinAny any){
	ObinTypeTrait* trait;

	CHECK_TRAIT(state, any, __equal__);

	return obin_tt_call(__hash__, state, any);
}

