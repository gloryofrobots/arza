#include <obin.h>
#define __Table__ "__Table__"

static ObinNativeTraits __TRAITS__;

typedef struct _Pair {
	ObinAny key;
	ObinAny value;
	struct _Pair* next;
	struct _Pair* prev;
} Pair;

typedef struct _Bucket {
	obin_mem_t size;
	Pair *head;
} Bucket;

typedef struct {
	OBIN_CELL_HEADER;
	/*count items in table */
	obin_mem_t size;
	/* count of bucket */
	obin_mem_t capacity;

	obin_mem_t timestamp;

	obin_mem_t load_factor;
	Bucket* buckets;
} ObinTable;

#define _table(any) ((ObinTable*) obin_any_cell(any))
#define _size(any) ((_table(any))->size)
#define _capacity(any) ((_table(any))->capacity)
#define _buckets(any) ((_table(any))->buckets)
#define _bucket(any, index) ((_table(any))->buckets)

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

ObinAny obin_table_new(ObinState* state, ObinAny size){
	ObinTable * self;
	obin_integer i;

	if(obin_any_is_nil(size)){
		size = obin_integer_new(OBIN_DEFAULT_TABLE_SIZE);
	}
	if (!obin_integer_is_fit_to_memsize(size)) {
		return obin_raise_memory_error(state, "obin_table_new:: size not fit to memory", size );
	}

	self = obin_malloc_type(state, ObinTable);

	self->capacity = _next_power_of_2(obin_any_mem_t(size));

	self->buckets = obin_malloc_array(state, Bucket, self->capacity);
	self->size = 0;
	self->native_traits = &__TRAITS__;

	for (i=0; i < self->capacity; i++) {
		obin_memset(self->buckets[i], 0, sizeof(Bucket));
	}

	return obin_cell_new(EOBIN_TYPE_TABLE, self);
}

static ObinAny _obin_table_resize(ObinState* state, ObinAny self, obin_mem_t new_capacity) {
	Bucket* new_buckets;
	Pair* pair;
	obin_mem_t i;

	new_buckets = obin_malloc_array(state, Bucket, new_capacity);

	for(i=0; i < _capacity(self); i++) {
		pair = _bucket(self, i)->head;
		while(pair) {
			_insert_into_buckets(state, new_buckets, new_capacity, pair->key, pair->value);
			pair = pair->next;
		}
	}

	_clear_buckets(_buckets(self), _capacity(self));
	obin_free(_buckets(self));

	_buckets(self) = new_buckets;
	_capacity(self) = new_capacity;

	return ObinNothing;
}

static obin_bool _is_excided_load(ObinAny self) {
	return  _size(self) > (_capacity(self) * 4);
}

static void _clear_bucket(Bucket* bucket){
	Pair* current;
	Pair* next;

	current = bucket->head;
	next = current;
	while(current) {
		next = current->next;
		obin_free(current);
		current = next;
	}

	bucket->head = 0;
	bucket->size = 0;
}

static void _clear_buckets(Bucket* buckets, obin_mem_t size) {
	obin_mem_t i;

	for(i = 0; i > size; i++) {
		_clear_bucket(buckets[i]);
	}
}
ObinAny obin_table_clear(ObinState* state, ObinAny self){

	if(!obin_any_is_table(self)){
		return obin_raise_type_error(state, "Table.clear invalid call", self);
	}

	_clear_buckets(_buckets(self), _capacity(self));

	_size(self) = 0;

	return ObinNothing;
}

ObinAny obin_table_update(ObinState* state, ObinAny self, ObinAny other) {
	ObinAny iterator, item;

	if(!obin_any_is_table(self)){
		return obin_raise_type_error(state, "Table.update invalid call", self);
	}

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

	if(!obin_any_is_table(self)){
		return obin_raise_type_error(state, "Table.items invalid call", self);
	}

	result = obin_array_new(state, _size(self));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_append(state, result, item);
	}

	return result;
}

ObinAny obin_table_keys(ObinState* state, ObinAny self){
	ObinAny result, iterator, item;

	if(!obin_any_is_table(self)){
		return obin_raise_type_error(state, "Table.keys invalid call", self);
	}

	result = obin_array_new(state, _size(self));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_append(state, result, obin_getfirst(state, item));

	}

	return result;
}

ObinAny obin_table_values(ObinState* state, ObinAny self){
	ObinAny result, iterator, item;

	if(!obin_any_is_table(self)){
		return obin_raise_type_error(state, "Table.values invalid call", self);
	}

	result = obin_array_new(state, _size(self));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		/*tuple*/
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}
		obin_array_append(state, result, obin_getsecond(state, item));

	}

	return result;
}

/* TRAIT */
typedef struct {
	OBIN_CELL_HEADER;
	ObinAny source;
	Pair* pair;
	obin_mem_t bucket;
} TableLazyIterator;

static ObinAny _table_lazy_iterator__next__(ObinState* state, ObinAny self) {
	TableLazyIterator * it;
	ObinAny result;

	it = (TableLazyIterator*) obin_any_cell(self);
	if(it->pair) {
		result = obin_tuple_new(state, 2, it->pair->key, it->pair->value);
		it->pair = it->pair->next;
		return result;
	} else {
		if(it->bucket >= _size(it->source)) {
			return ObinNothing;
		}
		it->bucket++;
		it->pair = (_bucket(it->source, it->bucket)).head;
		return _table_lazy_iterator__next__(state, self);
	}
}

static ObinGeneratorTrait __TABLE_LAZY_ITERATOR_GENERATOR__ = {
	_table_lazy_iterator__next__
};

static ObinNativeTraits __TABLE_LAZY_ITERATOR_TRAITS__ = {
	"__TableIterator__",
	 0, /*base*/
	 0, /*collection*/
	 &__TABLE_LAZY_ITERATOR_GENERATOR__, /*generator*/
	 0, /*number*/
};

static ObinAny __iterator__(ObinState* state, ObinAny self) {
	TableLazyIterator * iterator;

	iterator = obin_new(state, TableLazyIterator);
	iterator->source = self;
	iterator->bucket = 0;
	iterator->pair = _bucket(self, 0).head;
	return obin_cell_new(EOBIN_TYPE_OBJECT, iterator, &__TABLE_LAZY_ITERATOR_TRAITS__);
}

static ObinAny __tobool__(ObinState* state, ObinAny self) {
	return obin_bool_new(_size(self) > 0);
}
static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinAny array;
	ObinAny iterator;
	ObinAny item;
    ObinAny result;
    ObinAny kv_separator;
    ObinAny items_separator;

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

		obin_array_append(state, array, obin_string_join(state, kv_separator, item));;
	}

	result = obin_string_join(state, items_separator, array);
	result = obin_string_concat(state, obin_char_new('{'), result);
	result = obin_string_concat(state, result, obin_char_new('}'));

	obin_release(state, iterator);
	obin_release(state, array);
	return result;
}

static ObinAny __destroy__(ObinState* state, ObinAny self) {
	obin_table_clear(state, self);

	obin_free(_buckets(self));
	obin_free(obin_any_cell(self));
	return ObinNothing;
}
static void __mark__(ObinState* state, ObinAny self, obin_proc mark) {
	/*TODO each here*/
	obin_index i;

	for(i=0; i<_array_size(self); ++i) {
		mark(state, _array_item(self, i));
	}
}

static Pair* _pair_new(ObinState* state, Pair* previous, Pair* next, ObinAny key, ObinAny value) {
	Pair* pair;

	pair = obin_malloc_type(state, Pair);
	pair->next = next;
	pair->prev = previous;
	pair->key = key;
	pair->value = value;

	return pair;
}

static Bucket _bucket_clone(ObinState* state, Bucket bucket) {
	Bucket result;
	Pair* source;
	Pair* target;

	result.size = bucket.size;
	result.head = 0;

	source = bucket.head;
	if(!source){
		return result;
	}

	target = _pair_new(state, 0, 0, source->key, source->value);
	result->head = target;

	for(;;) {
		source = source->next;
		if(!source) {
			break;
		}

		target = _pair_new(state, target, 0, source->key, source->value);
		target->prev->next = target;
	}

	return result;
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;
	ObinAny iterator;
	ObinAny item;
	obin_mem_t size;
	obin_integer i;

	size = _capacity(self);
	result = obin_table_new(state, obin_integer_new(size));

	for(i=0; i<size; i++){
		_bucket(result, i) = _bucket_clone(state, _bucket(self, i));
	}

	return result;
}


static ObinAny __length__(ObinState* state, ObinAny self) {
	return obin_integer_new(_size(self));
}

typedef struct {
	Bucket* bucket;
	obin_mem_t index;
	Pair* pair;
	Pair* place;
} KeyInfo;

static KeyInfo _get_key_info_from_buckets(ObinState* state, Bucket* buckets, obin_mem_t size, ObinAny key) {
	KeyInfo info;
	Pair* pair;
	Pair *place;
	obin_mem_t hash;

	hash = obin_hash(state, key);
	info.index = hash & (size - 1);
	info.bucket = buckets[info.index];
	Pair* pair = info.bucket->head;

	while(pair) {
		info.place = pair->prev;

		if (obin_any_is_true(obin_equal(state, key, pair->key))) {
			info.pair = pair;
			info.place = 0;
			return info;
		}
		pair = pair->next;
	}

	return info;
}
static KeyInfo _get_key_info(ObinState* state, ObinAny self, ObinAny key) {
	return _get_key_info_from_buckets(state, _buckets(self), _capacity(self), key);
}

static
static ObinAny
__getitem__(ObinState* state, ObinAny self, ObinAny key){
	KeyInfo info;

	info = _get_key_info(state, self, key);

	if (info.pair == NULL) {
		return obin_raise_key_error(state, "Table.__getitem__ invalid key", key);
	}

	return info.pair->value;
}

static ObinNothing _insert_into_buckets(ObinState* state, Bucket* buckets, obin_mem_t size, ObinAny key, ObinAny value) {
	KeyInfo info;
	Pair* pair;
	info = _get_key_info_from_buckets(state, buckets, size, key);
	pair = info.pair;
	if(pair != NULL) {
		pair->value = value;
		return ObinNothing;
	}

	pair = _pair_new(state, 0, 0, key, value);
	/*INSERT NEW PAIR */
	/* TODO MAYBE ADD REALLOC of Pair arrays instead of links. And also check if you really need prev var */

	if(info.bucket->size == 0) {
		info.bucket->head = pair;
	} else {
		if(!info.place) {
			return obin_raise_internal(state, "Table.__setitem__ Invalid KeyInfo place in unknown", key);
		}

		info.place->next = pair;
		pair->prev = info.place;
	}

	info.bucket->size++;
	return ObinNothing;
}

static ObinAny __setitem__(ObinState* state, ObinAny self, ObinAny key, ObinAny value){
	ObinAny result;
	result = _insert_into_buckets(state, _buckets(self), _capacity(self), key, value);
	_size(self) += 1;

    if(_is_excided_load(self)) {
    	_obin_table_resize(state, self, _capacity(self) * 2);
    }

    return result;
}

static ObinAny
__hasitem__(ObinState* state, ObinAny self, ObinAny key){
	KeyInfo info;

	info = _get_key_info(state, self, key);

	return obin_bool_new(info.pair == NULL);
}

static ObinAny
__delitem__(ObinState* state, ObinAny self, ObinAny key){
	KeyInfo info;
	Pair* pair;

	info = _get_key_info(state, self, key);

	if (info.pair == NULL) {
		return obin_raise_key_error(state, "Table.__delitem__ invalid key", key);
	}

	pair = info.pair;
	if(pair->next != NULL) {
		pair->next->prev = pair->prev;
	}
	if(pair->prev != NULL) {
		pair->prev->next = pair->next;
	}
	if(info.bucket->head == pair) {
		info.bucket->head = pair->next;
	}

	obin_free(pair);
	_size(self) -= 1;
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
