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

	result = ogetitem(state, it->source, OInteger(it->current));
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

OAny OSequence_iterator(OState* state, OAny sequence){
	SequenceIterator * iterator;

	iterator = obin_new(state, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;
	iterator->length = (omem_t) OAny_toInt(olength(state, sequence));

	return OCell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__SEQUENCE_ITERATOR_BEHAVIOR__, ocells(state)->__Cell__);
}

OAny OCollection_compare(OState * state, OAny self, OAny other){
	OAny self_length;
	OAny other_length;
	OAny self_iterator;
	OAny other_iterator;
	OAny self_item;
	OAny other_item;
	OAny compare_result;

	self_length = olength(state, self);

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

	other_length = olength(state, other);

	if (OAny_toInt(self_length) < OAny_toInt(other_length)) {
		return ointegers(state)->Lesser;
	}

	if (OAny_toInt(self_length) > OAny_toInt(other_length)) {
		return ointegers(state)->Greater;
	}

	self_iterator = oiterator(state, self);
	other_iterator = oiterator(state, other);

	compare_result = ointegers(state)->Equal;

	while(OTRUE) {
		self_item = onext(state, self_iterator);
		other_item = onext(state, other_iterator);

		if(OBIN_IS_STOP_ITERATION(self_item) || OBIN_IS_STOP_ITERATION(other_item)){
			break;
		}

		compare_result = ocompare(state, self_item, other_item);
		if(OAny_isTrue(ois(state, compare_result, ointegers(state)->Equal))){
			break;
		}
	}

	orelease(state, self_iterator);
	orelease(state, other_iterator);
	return compare_result;
}
