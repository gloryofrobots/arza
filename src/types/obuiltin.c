#include <ointernal.h>

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
	return iterable->type_trait->__iter__(any);
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
		obin_raise_invalid_argument(state, "Method invokation error -> __destroy__ not exist", any);
	}

	return obin_type_call(any, __destroy__);
}
