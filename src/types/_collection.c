#include <core/omemory.h>
#include "ocollection.h"

typedef struct {
	OBIN_CELL_HEADER;
	ObinAny source;
	obin_mem_t current;
} SequenceIterator;

static ObinAny _sequence_iterator__next__(ObinState* state, ObinAny self) {
	SequenceIterator * it;
	ObinAny result;

	it = (SequenceIterator*) obin_any_cell(self);
	if(it->current >= _string_size(it->source)){
		return ObinInterrupt;
	}

	result = obin_getitem(state, it->source, obin_new_integer(it->current));
	it->current++;
	return result;
}

static ObinNativeTraits __SEQUENCE_ITERATOR_TRAITS__ = {
	 0, /*__tostring__,*/
	 0, /*__destroy__,*/
	 0, /*__clone__,*/
	 0, /*__compare__,*/
	 0, /*__hash__,*/

	 0, /*__iterator__,*/
	 0, /*__next__,*/
	 0, /*__length__,*/
	 0, /*__getitem__,*/
	 0, /*__setitem__,*/
	 0, /*__hasitem__,*/
	 _sequence_iterator__next__
};

ObinAny obin_sequence_iterator_new(ObinState* state, ObinAny sequence){
	SequenceIterator * iterator;

	if(!obin_can_it_be_collection(sequence)){
		obin_raise_type_error(state, "Collection expected", sequence);
	}

	iterator = obin_malloc_type(state, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;

	obin_cell_set_native_traits(iterator, __SEQUENCE_ITERATOR_TRAITS__);
	return obin_cell_new(iterator);
}

ObinAny obin_collection_compare(ObinState * state, ObinAny self, ObinAny other){
	ObinAny self_length;
	ObinAny other_length;
	ObinAny self_iterator;
	ObinAny other_iterator;
	ObinAny self_item;
	ObinAny other_item;
	ObinAny compare_result;

	self_length = obin_length(state, self);
	if(!obin_can_it_be_collection(self)){
		return obin_raise_type_error(state, "Collection.__compare__  collection expected", self);
	}

	if (!obin_can_it_be_collection(other)) {
		if(obin_any_integer(self_length) > 0){
			return ObinGreater;
		}

		if(obin_any_is_nil(other) || obin_any_is_false(other)) {
				return ObinEqual;
		}

		return ObinLesser;
	}

	other_length = obin_length(state, other);

	if (obin_any_integer(self_length) < obin_any_integer(other_length)) {
		return ObinLesser;
	}

	if (obin_any_integer(self_length) > obin_any_integer(other_length)) {
		return ObinGreater;
	}

	self_iterator = obin_iterator(state, self);
	other_iterator = obin_iterator(state, other);

	compare_result = ObinEqual;

	while(OTRUE) {
		self_item = obin_next(self_iterator);
		other_item = obin_next(other_iterator);

		if(obin_is_stop_iteration(self_item) || obin_is_stop_iteration(other_item)){
			break;
		}

		compare_result = obin_compare(self_item, other_item);
		if(!obin_any_is_equal(compare_result)){
			break;
		}
	}

	obin_destroy(self_iterator);
	obin_destroy(other_iterator);
	return compare_result;
}
