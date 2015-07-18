#include <obin.h>
#define __Table__ "__Table__"

#define _CHECK_SELF_TYPE(state, self, method) \
	if(!obin_any_is_array(self)) { \
		return obin_raise(state, obin_errors(state)->TypeError, \
				__Table__ #method "call from other type", self); \
	} \

/*TODO OPTIMIZE ITERATORS SO THEY DON'T CREATE ARRAYS AND BE COMPLETELY LAZY*/
static ObinNativeTraits __TRAITS__;

typedef struct {
	obin_bool isset;
	ObinAny key;
	ObinAny value;
} _ObinHashTableEntry;

typedef struct {
	OBIN_CELL_HEADER;
	_ObinHashTableEntry* body;
	obin_mem_t size;
	obin_mem_t capacity;
	obin_integer iter_count;
} ObinTable;

#define _table(any) ((ObinTable*) obin_any_cell(any))
#define _size(any) ((_table(any))->size)
#define _capacity(any) ((_table(any))->capacity)
#define _body(any) ((_table(any))->body)
#define _iter_count(any, index) ((_table(any))->iter_count)

static obin_mem_t _next_power_of_2(obin_mem_t v){
	v--;
	v |= v >> 1;
	v |= v >> 2;
	v |= v >> 4;
	v |= v >> 8;
	if(sizeof(obin_mem_t) > 16){
		v |= v >> 16;
	}
	if(sizeof(obin_mem_t) > 32){
		v |= v >> 32;
	}
	v++;
	return v;
}

static ObinAny __setitem__(ObinState* state, ObinAny self, ObinAny key, ObinAny value);

ObinAny obin_table_new(ObinState* state, ObinAny size){
	ObinTable * self;

	if(obin_any_is_nil(size)){
		size = obin_integer_new(OBIN_DEFAULT_TABLE_SIZE);
	}

	if (!obin_integer_is_fit_to_memsize(size)) {
		return obin_raise(state, obin_errors(state)->MemoryError,
				"obin_table_new:: size not fit to memory", size);
	}

	self = obin_new(state, ObinTable);

	self->capacity = _next_power_of_2(obin_any_mem_t(size));

	self->body = obin_malloc_array(state, _ObinHashTableEntry, self->capacity);
	self->size = 0;

	return obin_cell_new(EOBIN_TYPE_TABLE, (ObinCell*)self, &__TRAITS__);
}

static void _obin_table_resize(ObinState* state, ObinAny self, obin_mem_t new_capacity) {
	obin_mem_t i;
	obin_mem_t old_capacity = _capacity(self);
	_ObinHashTableEntry* old_body = _body(self);

	_body(self) = obin_malloc_array(state, _ObinHashTableEntry, new_capacity);
	_capacity(self) = new_capacity;

	for (i = 0; i < old_capacity; i++) {
		if (old_body[i].isset) {
			__setitem__(state, self, old_body[i].key, old_body[i].value);
		}
	}

	obin_free(state, old_body);
}

static obin_bool _is_excided_load(ObinAny self) {
	return (float)_size(self) / _capacity(self) > OBIN_TABLE_LOAD_FACTOR;
}

ObinAny obin_table_clear(ObinState* state, ObinAny self){
	obin_index i;

	_CHECK_SELF_TYPE(state, self, obin_table_clear);

	for (i = 0; i < _capacity(self); i++) {
		_body(self)[i].isset = OFALSE;
	}

	_size(self) = 0;

	return ObinNothing;
}

ObinAny obin_table_update(ObinState* state, ObinAny self, ObinAny other) {
	ObinAny iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_update);

	iterator = obin_iterator(state, other);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}

		obin_setitem(state, self,
				obin_getfirst(state, item),
				obin_getsecond(state, item));
	}

	return ObinNothing;
}

ObinAny obin_table_items(ObinState* state, ObinAny self){
	ObinAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_items);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_push(state, result, item);
	}

	return result;
}

ObinAny obin_table_keys(ObinState* state, ObinAny self){
	ObinAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_keys);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_push(state, result, obin_getfirst(state, item));

	}

	return result;
}

ObinAny obin_table_values(ObinState* state, ObinAny self){
	ObinAny result, iterator, item;

	_CHECK_SELF_TYPE(state, self, obin_table_values);

	result = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_push(state, result, obin_getsecond(state, item));

	}

	return result;
}

/* TRAIT */
typedef struct {
	OBIN_CELL_HEADER;
	ObinAny source;
	obin_index index;
} TableIterator;

static ObinAny __iterator__next__(ObinState* state, ObinAny self) {
	TableIterator * it;
	ObinAny result = ObinNothing;

	it = (TableIterator*) obin_any_cell(self);

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

static ObinGeneratorTrait __TABLE_ITERATOR_GENERATOR__ = {
	__iterator__next__
};

static ObinNativeTraits __TABLE_ITERATOR_TRAITS__ = {
	"__TableIterator__",
	 0, /*base*/
	 0, /*collection*/
	 &__TABLE_ITERATOR_GENERATOR__, /*generator*/
	 0, /*number*/
};

static ObinAny __iterator__(ObinState* state, ObinAny self) {
	TableIterator * iterator;

	_CHECK_SELF_TYPE(state, self, __iterator__);

	iterator = obin_new(state, TableIterator);
	iterator->source = self;
	iterator->index = 0;
	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*)iterator, &__TABLE_ITERATOR_TRAITS__);
}

static ObinAny __tobool__(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, __tobool__);

	return obin_bool_new(_size(self) > 0);
}

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinAny array;
	ObinAny iterator;
	ObinAny item;
    ObinAny result;
    ObinAny kv_separator;
    ObinAny items_separator;

	_CHECK_SELF_TYPE(state, self, __tostring__);

    kv_separator = obin_string_new(state, ": ");
    items_separator = obin_string_new(state, ", ");

	array = obin_array_new(state, obin_integer_new(_size(self)));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}

		obin_array_push(state, array, obin_string_join(state, kv_separator, item));
	}

	result = obin_string_join(state, items_separator, array);
	result = obin_string_concat(state, obin_char_new('{'), result);
	result = obin_string_concat(state, result, obin_char_new('}'));

	obin_release(state, iterator);
	obin_release(state, array);
	return result;
}

static void __destroy__(ObinState* state, ObinCell* table) {
	ObinTable* self = (ObinTable*) table;
	obin_free(state, self->body);
	self->body = NULL;
}

static void __mark__(ObinState* state, ObinAny self, obin_proc mark) {
	obin_index i;

	for(i = 0; i < _capacity(self); ++i) {
		if(_body(self)[i].isset) {
			mark(state, _body(self)[i].key);
			mark(state, _body(self)[i].value);
		}
	}
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;
	obin_mem_t capacity;

	_CHECK_SELF_TYPE(state, self, __clone__);

	capacity = _capacity(self);
	result = obin_table_new(state, obin_integer_new(capacity));
	obin_memcpy(_body(result), _body(self), sizeof(_ObinHashTableEntry) * capacity);
	return result;
}

static ObinAny __length__(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_size(self));
}

/**
 * Find an available slot for the given key, using linear probing.
 */
obin_index _find_slot(ObinState* state, ObinAny self, ObinAny key)
{
	obin_integer hash = obin_any_integer(obin_hash(state, key));
	obin_index index;

	index =  hash % _capacity(self);

	while (_body(self)[index].isset
			&&  obin_any_is_true(obin_equal(state, _body(self)[index].key, key))) {
		index = (index + 1) % _capacity(self);
	}
	return index;
}

static ObinAny
__getitem__(ObinState* state, ObinAny self, ObinAny key){
	obin_integer index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __getitem__);

	if (!_body(self)[index].isset) {
		obin_raise(state, obin_errors(state)->KeyError, __Table__ ".__getitem__ invalid key", key);
	}

	return _body(self)[index].value;
}

static ObinAny __setitem__(ObinState* state, ObinAny self, ObinAny key, ObinAny value){

	_CHECK_SELF_TYPE(state, self, __getitem__);

	obin_integer index = _find_slot(state, self, key);
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

static ObinAny
__hasitem__(ObinState* state, ObinAny self, ObinAny key){
	obin_index index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __hasitem__);

	return obin_bool_new(_body(self)[index].isset);
}

static ObinAny
__delitem__(ObinState* state, ObinAny self, ObinAny key){
	obin_index index = _find_slot(state, self, key);

	_CHECK_SELF_TYPE(state, self, __delitem__);

	if (!_body(self)[index].isset) {
		obin_raise(state, obin_errors(state)->KeyError, __Table__ "__delitem__ unknown key", key);
	}

	_body(self)[index].isset = OFALSE;
	_size(self)--;

	return ObinNothing;
}

static ObinCollectionTrait __COLLECTION__ = {
	 __iterator__,
	 __length__,
	 __getitem__,
	 __setitem__,
	 __hasitem__,
	 __delitem__,
} ;

static ObinBaseTrait __BASE__ = {
	 __tostring__,
	 __tobool__,
	 __destroy__,
	 __clone__,
	 obin_collection_compare,
	 0,
	 __mark__
};

static ObinNativeTraits __TRAITS__ = {
	__Table__,
	 /*base*/
	 &__BASE__,
	 &__COLLECTION__, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};
