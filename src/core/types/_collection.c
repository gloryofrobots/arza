#include <obin.h>

/*TODO Avoid infinite recursion in _tostring__ and others in recursive vollections */

OCELL_DECLARE(SequenceIterator,
	OAny source;
	omem_t current;
	omem_t length;
);

static OAny __si__next__(OState* S, OAny self) {
	SequenceIterator * it;
	OAny result;

	it = (SequenceIterator*) OAny_cellVal(self);
	if(it->current >= it->length){
		return ObinNothing;
	}

	result = ogetitem(S, it->source, OInteger(it->current));
	it->current++;
	return result;
}

OBEHAVIOR_DEFINE(__SEQUENCE_ITERATOR_BEHAVIOR__,
		"__SequenceIterator__",
		OBEHAVIOR_MEMORY_NULL,
		OBEHAVIOR_BASE_NULL,
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR(__si__next__),
		OBEHAVIOR_NUMBER_NULL
);

OAny OSequence_iterator(OState* S, OAny sequence){
	SequenceIterator * iterator;

	iterator = obin_new(S, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;
	iterator->length = (omem_t) OAny_intVal(olength(S, sequence));

	return OCell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__SEQUENCE_ITERATOR_BEHAVIOR__, ocells(S)->__Cell__);
}

OAny OCollection_compare(OState * S, OAny self, OAny other){
	OAny self_length;
	OAny other_length;
	OAny self_iterator;
	OAny other_iterator;
	OAny self_item;
	OAny other_item;
	OAny compare_result;

	self_length = olength(S, self);

	/*TODO ADD TYPE CHECK HERE FOR __COLLECTION__ cell*/
	if(!OAny_isCell(other)){
		if(OAny_intVal(self_length) > 0){
			return ointegers(S)->Greater;
		}

		if(OAny_isNil(other) || OAny_isFalse(other)) {
				return ointegers(S)->Equal;
		}

		return ointegers(S)->Lesser;
	}

	other_length = olength(S, other);

	if (OAny_intVal(self_length) < OAny_intVal(other_length)) {
		return ointegers(S)->Lesser;
	}

	if (OAny_intVal(self_length) > OAny_intVal(other_length)) {
		return ointegers(S)->Greater;
	}

	self_iterator = oiterator(S, self);
	other_iterator = oiterator(S, other);

	compare_result = ointegers(S)->Equal;

	while(OTRUE) {
		self_item = onext(S, self_iterator);
		other_item = onext(S, other_iterator);

		if(OBIN_IS_STOP_ITERATION(self_item) || OBIN_IS_STOP_ITERATION(other_item)){
			break;
		}

		compare_result = ocompare(S, self_item, other_item);
		if(OAny_isTrue(ois(S, compare_result, ointegers(S)->Equal))){
			break;
		}
	}

	orelease(S, self_iterator);
	orelease(S, other_iterator);
	return compare_result;
}
