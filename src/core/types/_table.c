#include <obin.h>
#define __TypeName__ "__Table__"

#define _CHECK_SELF_TYPE(state, self, method) \
	if(!OAny_isTable(self)) { \
		return obin_raise(state, oerrors(state)->TypeError, \
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

static OAny __setitem__(OState* state, OAny self, OAny key, OAny value);

OAny obin_table_new(OState* state, OAny size){
	ObinTable * self;

	if(OAny_isNil(size)){
		size = obin_integer_new(OBIN_DEFAULT_TABLE_SIZE);
	}

	if (!OInt_isFitToMemsize(size)) {
		return obin_raise(state, oerrors(state)->MemoryError,
				"obin_table_new:: size not fit to memory", size);
	}

	self = obin_new(state, ObinTable);

	self->capacity = _next_power_of_2(OAny_toMem_t(size));

	self->body = obin_malloc_array(state, _ObinHashTableEntry, self->capacity);
	self->size = 0;

	return obin_cell_new(EOBIN_TYPE_TABLE, (OCell*)self, &__BEHAVIOR__, ocells(state)->__Table__);
}

static void _obin_table_resize(OState* state, OAny self, omem_t new_capacity) {
	omem_t i;
	omem_t old_capacity = _capacity(self);
	_ObinHashTableEntry* old_body = _body(self);

	_body(self) = obin_malloc_array(state, _ObinHashTableEntry, new_capacity);
	_capacity(self) = new_capacity;

	for (i = 0; i < old_capacity; i++) {
		if (old_body[i].isset) {
			__setitem__(state, self, old_body[i].key, old_body[i].value);
		}
	}

	obin_memory_free(state, old_body);
}

static obool _is_excided_load(OAny self) {
	return (float)_size(self) / _capacity(self) > OBIN_TABLE_LOAD_FACTOR;
}

OAny obin_table_clear(OState* state, OAny self){
	oindex_t i;

	_CHECK_SELF_TYPE(state, self, obin_table_clear);

	for (i = 0; i < _capacity(self); i++) {
		_body(self)[i].isset = OFALSE;
	}

	_size(self) = 0;

	return ObinNothing;
}

OAny obin_table_update(OState* state, OAny self, OAny other) {
	OAny iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_update);

	iterator = obin_iterator(state, other);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}

		obin_setitem(state, self,
				obin_getfirst(state, item),
				obin_getsecond(state, item));
	}

	return ObinNothing;
}

OAny obin_table_items(OState* state, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_items);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		obin_array_push(state, result, item);
	}

	return result;
}

OAny obin_table_keys(OState* state, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_keys);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		obin_array_push(state, result, obin_getfirst(state, item));

	}

	return result;
}

OAny obin_table_values(OState* state, OAny self){
	OAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_values);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}
		obin_array_push(state, result, obin_getsecond(state, item));

	}

	return result;
}

/* TRAIT */
typedef struct {
	OCELL_HEADER;
	OAny source;
	oindex_t index;
} TableIterator;

static OAny __iterator__next__(OState* state, OAny self) {
	TableIterator * it;
	OAny result = ObinNothing;

	it = (TableIterator*) OAny_toCell(self);

	while(it->index < _capacity(it->source)) {
		if(_body(self)[it->index].isset) {
			result = obin_tuple_pack(state, 2,
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
		OBEHAVIOR_NUMBER_CAST_NULL,
		OBEHAVIOR_NUMBER_OPERATIONS_NULL
);

static OAny __iterator__(OState* state, OAny self) {
	TableIterator * iterator;

	_CHECK_SELF_TYPE(state, self, __iterator__);

	iterator = obin_new(state, TableIterator);
	iterator->source = self;
	iterator->index = 0;
	return obin_cell_new(EOBIN_TYPE_CELL, (OCell*)iterator, &__TABLE_ITERATOR_BEHAVIOR__, ObinNil);
}

static OAny __tobool__(OState* state, OAny self) {
	_CHECK_SELF_TYPE(state, self, __tobool__);

	return obin_bool_new(_size(self) > 0);
}

static OAny __tostring__(OState* state, OAny self) {
	OAny array;
	OAny iterator;
	OAny item;
    OAny result;
    OAny kv_separator;
    OAny items_separator;

	_CHECK_SELF_TYPE(state, self, __tostring__);

    kv_separator = obin_string_new(state, ": ");
    items_separator = obin_string_new(state, ", ");

	array = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (OBIN_IS_STOP_ITERATION(item)) {
			break;
		}

		obin_array_push(state, array, obin_string_join(state, kv_separator, item));
	}

	result = obin_string_join(state, items_separator, array);
	result = obin_add(state, obin_char_new('{'), result);
	result = obin_add(state, result, obin_char_new('}'));

	obin_release(state, iterator);
	obin_release(state, array);
	return result;
}

static void __destroy__(OState* state, OCell* table) {
	ObinTable* self = (ObinTable*) table;
	obin_memory_free(state, self->body);
	self->body = NULL;
}

static void __mark__(OState* state, OAny self, ofunc_1 mark) {
	oindex_t i;

	for(i = 0; i < _capacity(self); ++i) {
		if(_body(self)[i].isset) {
			mark(state, _body(self)[i].key);
			mark(state, _body(self)[i].value);
		}
	}
}

static OAny __clone__(OState* state, OAny self) {
	OAny result;
	omem_t capacity;

	_CHECK_SELF_TYPE(state, self, __clone__);

	capacity = _capacity(self);
	result = obin_table_new(state, obin_integer_new(capacity));
	obin_memcpy(_body(result), _body(self), sizeof(_ObinHashTableEntry) * capacity);
	return result;
}

static OAny __length__(OState* state, OAny self) {
	_CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_size(self));
}

/**
 * Find an available slot for the given key, using linear probing.
 */
oindex_t _find_slot(OState* state, OAny self, OAny key)
{
	oint hash = OAny_toInt(obin_hash(state, key));
	oindex_t index;

	index =  hash % _capacity(self);

	while (_body(self)[index].isset
			&&  OAny_isTrue(obin_equal(state, _body(self)[index].key, key))) {
		index = (index + 1) % _capacity(self);
	}
	return index;
}

static OAny
__getitem__(OState* state, OAny self, OAny key){
	oint index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __getitem__);

	if (!_body(self)[index].isset) {
		obin_raise(state, oerrors(state)->KeyError, __TypeName__ ".__getitem__ invalid key", key);
	}

	return _body(self)[index].value;
}

static OAny __setitem__(OState* state, OAny self, OAny key, OAny value){

	_CHECK_SELF_TYPE(state, self, __getitem__);

	oint index = _find_slot(state, self, key);
	if (_body(self)[index].isset) {
		/* Entry exists; update it. */
		_body(self)[index].value = value;
	} else {
		_size(self)++;
		/* Create a new  entry */

		if (_is_excided_load(self)) {
			/* Resize the hash table */
			_obin_table_resize(state, self, _capacity(self) * 2);
			index = _find_slot(state, self, key);
		}
		_body(self)[index].key = key;
		_body(self)[index].value = value;
	}
	return ObinNothing;
}

static OAny
__hasitem__(OState* state, OAny self, OAny key){
	oindex_t index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __hasitem__);

	return obin_bool_new(_body(self)[index].isset);
}

static OAny
__delitem__(OState* state, OAny self, OAny key){
	oindex_t index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __delitem__);

	if (!_body(self)[index].isset) {
		obin_raise(state, oerrors(state)->KeyError, __TypeName__ "__delitem__ unknown key", key);
	}

	_body(self)[index].isset = OFALSE;
	_size(self)--;

	return ObinNothing;
}

obool obin_module_table_init(OState* state) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__destroy__ = __destroy__;
	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = obin_collection_compare;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__delitem__ = __delitem__;

	ocells(state)->__Table__ = obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, ocells(state)->__Cell__);

	return OTRUE;
}
