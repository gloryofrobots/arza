#include <obin.h>

/*TODO Avoid infinite recursion in _tostring__ and others in recursive vollections */

typedef struct {
	OBIN_CELL_HEADER;
	ObinAny source;
	obin_mem_t current;
	obin_mem_t length;
} SequenceIterator;

static ObinAny __si__next__(ObinState* state, ObinAny self) {
	SequenceIterator * it;
	ObinAny result;

	it = (SequenceIterator*) obin_any_cell(self);
	if(it->current >= it->length){
		return ObinNothing;
	}

	result = obin_getitem(state, it->source, obin_integer_new(it->current));
	it->current++;
	return result;
}

ObinGeneratorTrait __SI_GEN_TRAIT__  = {
		__si__next__
};

ObinNativeTraits __SI_TRAIT__ = {
	"SequenceIterator",

	0, /*base*/
	0, /* collection */
	&__SI_GEN_TRAIT__,
	0, /*number */
};

static obin_bool _is_collection(ObinAny any) {
	return (obin_any_cell(any)->native_traits != NULL &&
			obin_any_cell(any)->native_traits->collection != NULL);
}

ObinAny obin_sequence_iterator_new(ObinState* state, ObinAny sequence){
	SequenceIterator * iterator;
	if(!obin_any_is_cell(sequence)) {
		obin_raise(state, obin_errors(state)->TypeError,
				"Cell type expected", sequence);
	}

	if(!_is_collection(sequence)){
		obin_raise(state, obin_errors(state)->TypeError,
				"Collection expected", sequence);
	}

	iterator = obin_malloc_type(state, SequenceIterator);
	iterator->source = sequence;
	iterator->current = 0;
	iterator->length = (obin_mem_t) obin_any_integer(obin_length(state, sequence));

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*)iterator, &__SI_TRAIT__);
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

	if(!_is_collection(self)){
		obin_raise(state, obin_errors(state)->TypeError,
				"Collection.__compare__ expected", self);
	}

	if(!_is_collection(other)){
		if(obin_any_integer(self_length) > 0){
			return obin_integers(state)->Greater;
		}

		if(obin_any_is_nil(other) || obin_any_is_false(other)) {
				return obin_integers(state)->Equal;
		}

		return obin_integers(state)->Lesser;
	}

	other_length = obin_length(state, other);

	if (obin_any_integer(self_length) < obin_any_integer(other_length)) {
		return obin_integers(state)->Lesser;
	}

	if (obin_any_integer(self_length) > obin_any_integer(other_length)) {
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
		if(obin_any_is_true(obin_is(state, compare_result, obin_integers(state)->Equal))){
			break;
		}
	}

	obin_release(state, self_iterator);
	obin_release(state, other_iterator);
	return compare_result;
}
