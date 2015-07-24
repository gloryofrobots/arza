#include <obin.h>

/*TODO Avoid infinite recursion in _tostring__ and others in recursive vollections */

OBIN_DECLARE_CELL(SequenceIterator,
	ObinAny source;
	obin_mem_t current;
	obin_mem_t length;
);

static ObinAny __si__next__(ObinState* state, ObinAny self) {
	SequenceIterator * it;
	ObinAny result;

	it = (SequenceIterator*) OAny_toCell(self);
	if(it->current >= it->length){
		return ObinNothing;
	}

	result = obin_getitem(state, it->source, obin_integer_new(it->current));
	it->current++;
	return result;
}

OBIN_BEHAVIOR_DEFINE(__SEQUENCE_ITERATOR_BEHAVIOR__,
		"__SequenceIterator__",
		OBIN_BEHAVIOR_MEMORY_NULL,
		OBIN_BEHAVIOR_BASE_NULL,
		OBIN_BEHAVIOR_COLLECTION_NULL,
		OBIN_BEHAVIOR_GENERATOR(__si__next__),
		OBIN_BEHAVIOR_NUMBER_CAST_NULL,
		OBIN_BEHAVIOR_NUMBER_OPERATIONS_NULL
);

ObinAny obin_sequence_iterator_new(ObinState* state, ObinAny sequence){
	SequenceIterator * iterator;

	iterator = obin_new(state, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;
	iterator->length = (obin_mem_t) OAny_toInt(obin_length(state, sequence));

	return obin_cell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__SEQUENCE_ITERATOR_BEHAVIOR__, obin_cells(state)->__Cell__);
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

	/*TODO ADD TYPE CHECK HERE FOR __COLLECTION__ cell*/
	if(!obin_any_is_cell(other)){
		if(OAny_toInt(self_length) > 0){
			return obin_integers(state)->Greater;
		}

		if(OAny_isNil(other) || OAny_isFalse(other)) {
				return obin_integers(state)->Equal;
		}

		return obin_integers(state)->Lesser;
	}

	other_length = obin_length(state, other);

	if (OAny_toInt(self_length) < OAny_toInt(other_length)) {
		return obin_integers(state)->Lesser;
	}

	if (OAny_toInt(self_length) > OAny_toInt(other_length)) {
		return obin_integers(state)->Greater;
	}

	self_iterator = obin_iterator(state, self);
	other_iterator = obin_iterator(state, other);

	compare_result = obin_integers(state)->Equal;

	while(OTRUE) {
		self_item = obin_next(state, self_iterator);
		other_item = obin_next(state, other_iterator);

		if(obin_is_stop_iteration(self_item) || obin_is_stop_iteration(other_item)){
			break;
		}

		compare_result = obin_compare(state, self_item, other_item);
		if(OAny_isTrue(obin_is(state, compare_result, obin_integers(state)->Equal))){
			break;
		}
	}

	obin_release(state, self_iterator);
	obin_release(state, other_iterator);
	return compare_result;
}
