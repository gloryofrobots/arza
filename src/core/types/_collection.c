#include <obin.h>

/*TODO Avoid infinite recursion in _tostring__ and others in recursive vollections */

OCELL_DECLARE(SequenceIterator,
	OAny source;
	omem_t current;
	omem_t length;
);

static OAny __si__next__(OState* state, OAny self) {
	SequenceIterator * it;
	OAny result;

	it = (SequenceIterator*) OAny_toCell(self);
	if(it->current >= it->length){
		return ObinNothing;
	}

	result = obin_getitem(state, it->source, obin_integer_new(it->current));
	it->current++;
	return result;
}

OBEHAVIOR_DEFINE(__SEQUENCE_ITERATOR_BEHAVIOR__,
		"__SequenceIterator__",
		OBEHAVIOR_MEMORY_NULL,
		OBEHAVIOR_BASE_NULL,
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR(__si__next__),
		OBEHAVIOR_NUMBER_CAST_NULL,
		OBEHAVIOR_NUMBER_OPERATIONS_NULL
);

OAny obin_sequence_iterator_new(OState* state, OAny sequence){
	SequenceIterator * iterator;

	iterator = obin_new(state, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;
	iterator->length = (omem_t) OAny_toInt(obin_length(state, sequence));

	return obin_cell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__SEQUENCE_ITERATOR_BEHAVIOR__, ocells(state)->__Cell__);
}

OAny obin_collection_compare(OState * state, OAny self, OAny other){
	OAny self_length;
	OAny other_length;
	OAny self_iterator;
	OAny other_iterator;
	OAny self_item;
	OAny other_item;
	OAny compare_result;

	self_length = obin_length(state, self);

	/*TODO ADD TYPE CHECK HERE FOR __COLLECTION__ cell*/
	if(!OAny_isCell(other)){
		if(OAny_toInt(self_length) > 0){
			return ointegers(state)->Greater;
		}

		if(OAny_isNil(other) || OAny_isFalse(other)) {
				return ointegers(state)->Equal;
		}

		return ointegers(state)->Lesser;
	}

	other_length = obin_length(state, other);

	if (OAny_toInt(self_length) < OAny_toInt(other_length)) {
		return ointegers(state)->Lesser;
	}

	if (OAny_toInt(self_length) > OAny_toInt(other_length)) {
		return ointegers(state)->Greater;
	}

	self_iterator = obin_iterator(state, self);
	other_iterator = obin_iterator(state, other);

	compare_result = ointegers(state)->Equal;

	while(OTRUE) {
		self_item = obin_next(state, self_iterator);
		other_item = obin_next(state, other_iterator);

		if(OBIN_IS_STOP_ITERATION(self_item) || OBIN_IS_STOP_ITERATION(other_item)){
			break;
		}

		compare_result = obin_compare(state, self_item, other_item);
		if(OAny_isTrue(obin_is(state, compare_result, ointegers(state)->Equal))){
			break;
		}
	}

	obin_release(state, self_iterator);
	obin_release(state, other_iterator);
	return compare_result;
}
