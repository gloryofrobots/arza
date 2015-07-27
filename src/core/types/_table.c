#include <obin.h>
#define __TypeName__ "__Table__"

#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isTable(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__ #method "call from other type", self); \
	} \

/*TODO OPTIMIZE ITERATORS SO THEY DON'T CREATE ARRAYS AND BE COMPLETELY LAZY*/
static OBehavior __BEHAVIOR__;

typedef struct {
	obool isset;
	OAny key;
	OAny value;
} _ObinHashTableEntry;

typedef struct {
	OCELL_HEADER;
	_ObinHashTableEntry* body;
	omem_t size;
	omem_t capacity;
	oint iter_count;
} ObinTable;

#define _table(any) ((ObinTable*) OAny_toCell(any))
#define _size(any) ((_table(any))->size)
#define _capacity(any) ((_table(any))->capacity)
#define _body(any) ((_table(any))->body)
#define _iter_count(any, index) ((_table(any))->iter_count)

static omem_t _next_power_of_2(omem_t v){
	v--;
	v |= v >> 1;
	v |= v >> 2;
	v |= v >> 4;
	v |= v >> 8;
	if(sizeof(omem_t) > 16){
		v |= v >> 16;
	}
	if(sizeof(omem_t) > 32){
		v |= v >> 32;
	}
	v++;
	return v;
}

static OAny __setitem__(OState* S, OAny self, OAny key, OAny value);

OAny OTable(OState* S, OAny size){
	ObinTable * self;

	if(OAny_isNil(size)){
		size = OInteger(OBIN_DEFAULT_TABLE_SIZE);
	}

	if (!OInt_isFitToMemsize(size)) {
		return oraise(S, oerrors(S)->MemoryError,
				"obin_table_new:: size not fit to memory", size);
	}

	self = obin_new(S, ObinTable);

	self->capacity = _next_power_of_2(OAny_toMem_t(size));

	self->body = omemory_malloc_array(S, _ObinHashTableEntry, self->capacity);
	self->size = 0;

	return OCell_new(EOBIN_TYPE_TABLE, (OCell*)self, &__BEHAVIOR__, ocells(S)->__Table__);
}

static void _obin_table_resize(OState* S, OAny self, omem_t new_capacity) {
	omem_t i;
	omem_t old_capacity = _capacity(self);
	_ObinHashTableEntry* old_body = _body(self);

	_body(self) = omemory_malloc_array(S, _ObinHashTableEntry, new_capacity);
	_capacity(self) = new_capacity;

	for (i = 0; i < old_capacity; i++) {
		if (old_body[i].isset) {
			__setitem__(S, self, old_body[i].key, old_body[i].value);
		}
	}

	omemory_free(S, old_body);
}

static obool _is_excided_load(OAny self) {
	return (float)_size(self) / _capacity(self) > OBIN_TABLE_LOAD_FACTOR;
}

OAny OTable_clear(OState* S, OAny self){
	oindex_t i;

	_CHECK_SELF_TYPE(S, self, OTable_clear);

	for (i = 0; i < _capacity(self); i++) {
		_body(self)[i].isset = OFALSE;
	}

	_size(self) = 0;

	return ObinNothing;
}

OAny OTable_merge(OState* S, OAny self, OAny other) {
	OAny iterator, item;

	_CHECK_SELF_TYPE(S, self, OTable_clear);

	iterator = oiterator(S, other);

	while (OTRUE) {
		/*tuple*/
		item = onext(S, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}

		osetitem(S, self,
				ogetfirst(S, item),
				ogetsecond(S, item));
	}

	return ObinNothing;
}

OAny OTable_items(OState* S, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(S, self, OTable_items);

	result = OArray(S, OInteger(_size(self)));

	iterator = oiterator(S, self);

	while (OTRUE) {
		/*tuple*/
		item = onext(S, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		OArray_push(S, result, item);
	}

	return result;
}

OAny OTable_keys(OState* S, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(S, self, OTable_keys);

	result = OArray(S, OInteger(_size(self)));

	iterator = oiterator(S, self);

	while (OTRUE) {
		/*tuple*/
		item = onext(S, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		OArray_push(S, result, ogetfirst(S, item));

	}

	return result;
}

OAny OTable_values(OState* S, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(S, self, OTable_values);

	result = OArray(S, OInteger(_size(self)));

	iterator = oiterator(S, self);

	while (OTRUE) {
		/*tuple*/
		item = onext(S, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		OArray_push(S, result, ogetsecond(S, item));

	}

	return result;
}

/* TRAIT */
typedef struct {
	OCELL_HEADER;
	OAny source;
	oindex_t index;
} TableIterator;

static OAny __iterator__next__(OState* S, OAny self) {
	TableIterator * it;
	OAny result = ObinNothing;

	it = (TableIterator*) OAny_toCell(self);

	while(it->index < _capacity(it->source)) {
		if(_body(self)[it->index].isset) {
			result = OTuple(S, 2,
					_body(it->source)[it->index].key,
					_body(it->source)[it->index].key);
			it->index++;
			break;
		}

		it->index++;
	}

	return result;
}

OBEHAVIOR_DEFINE(__TABLE_ITERATOR_BEHAVIOR__,
		"__TableIterator__",
		OBEHAVIOR_MEMORY_NULL,
		OBEHAVIOR_BASE_NULL,
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR(__iterator__next__),
		OBEHAVIOR_NUMBER_NULL
);

static OAny __iterator__(OState* S, OAny self) {
	TableIterator * iterator;

	_CHECK_SELF_TYPE(S, self, __iterator__);

	iterator = obin_new(S, TableIterator);
	iterator->source = self;
	iterator->index = 0;
	return OCell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__TABLE_ITERATOR_BEHAVIOR__, ObinNil);
}

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);

	return OBool(_size(self) > 0);
}

static OAny __tostring__(OState* S, OAny self) {
	OAny array;
	OAny iterator;
	OAny item;
    OAny result;
    OAny kv_separator;
    OAny items_separator;

	_CHECK_SELF_TYPE(S, self, __tostring__);

    kv_separator = OString(S, ": ");
    items_separator = OString(S, ", ");

	array = OArray(S, OInteger(_size(self)));

	iterator = oiterator(S, self);

	while (OTRUE) {
		/*tuple*/
		item = onext(S, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}

		OArray_push(S, array, OString_join(S, kv_separator, item));
	}

	result = OString_join(S, items_separator, array);
	result = oadd(S, OChar_new('{'), result);
	result = oadd(S, result, OChar_new('}'));

	orelease(S, iterator);
	orelease(S, array);
	return result;
}

static void __destroy__(OState* S, OCell* table) {
	ObinTable* self = (ObinTable*) table;
	omemory_free(S, self->body);
	self->body = NULL;
}

static void __mark__(OState* S, OAny self, ofunc_1 mark) {
	oindex_t i;

	for(i = 0; i < _capacity(self); ++i) {
		if(_body(self)[i].isset) {
			mark(S, _body(self)[i].key);
			mark(S, _body(self)[i].value);
		}
	}
}

static OAny __clone__(OState* S, OAny self) {
	OAny result;
	omem_t capacity;

	_CHECK_SELF_TYPE(S, self, __clone__);

	capacity = _capacity(self);
	result = OTable(S, OInteger(capacity));
	omemcpy(_body(result), _body(self), sizeof(_ObinHashTableEntry) * capacity);
	return result;
}

static OAny __length__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __length__);

	return OInteger(_size(self));
}

/**
 * Find an available slot for the given key, using linear probing.
 */
oindex_t _find_slot(OState* S, OAny self, OAny key)
{
	oint hash = OAny_toInt(ohash(S, key));
	oindex_t index;

	index =  hash % _capacity(self);

	while (_body(self)[index].isset
			&&  OAny_isTrue(oequal(S, _body(self)[index].key, key))) {
		index = (index + 1) % _capacity(self);
	}
	return index;
}

static OAny
__getitem__(OState* S, OAny self, OAny key){
	oint index = _find_slot(S, self, key);

	_CHECK_SELF_TYPE(S, self, __getitem__);

	if (!_body(self)[index].isset) {
		oraise(S, oerrors(S)->KeyError, __TypeName__ ".__getitem__ invalid key", key);
	}

	return _body(self)[index].value;
}

static OAny __setitem__(OState* S, OAny self, OAny key, OAny value){

	_CHECK_SELF_TYPE(S, self, __getitem__);

	oint index = _find_slot(S, self, key);
	if (_body(self)[index].isset) {
		/* Entry exists; update it. */
		_body(self)[index].value = value;
	} else {
		_size(self)++;
		/* Create a new  entry */

		if (_is_excided_load(self)) {
			/* Resize the hash table */
			_obin_table_resize(S, self, _capacity(self) * 2);
			index = _find_slot(S, self, key);
		}
		_body(self)[index].key = key;
		_body(self)[index].value = value;
	}
	return ObinNothing;
}

static OAny
__hasitem__(OState* S, OAny self, OAny key){
	oindex_t index = _find_slot(S, self, key);

	_CHECK_SELF_TYPE(S, self, __hasitem__);

	return OBool(_body(self)[index].isset);
}

static OAny
__delitem__(OState* S, OAny self, OAny key){
	oindex_t index = _find_slot(S, self, key);

	_CHECK_SELF_TYPE(S, self, __delitem__);

	if (!_body(self)[index].isset) {
		oraise(S, oerrors(S)->KeyError, __TypeName__ "__delitem__ unknown key", key);
	}

	_body(self)[index].isset = OFALSE;
	_size(self)--;

	return ObinNothing;
}

obool otable_init(OState* S) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__destroy__ = __destroy__;
	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = OCollection_compare;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__delitem__ = __delitem__;

	ocells(S)->__Table__ = OCell_new(EOBIN_TYPE_CELL,
			obin_new(S, OCell), &__BEHAVIOR__, ocells(S)->__Cell__);

	return OTRUE;
}
