#include <obin.h>
#define __TypeName__ "__Array__"

OBIN_DECLARE_CELL(ObinArray,
	obin_mem_t size;
	obin_mem_t capacity;
	ObinAny* data;
);

static ObinBehavior __BEHAVIOR__ = {0};

#define _CHECK_SELF_TYPE(state, self, method) \
	if(!obin_any_is_array(self)) { \
		return obin_raise(state, obin_errors(state)->TypeError, \
				__TypeName__ #method "call from other type", self); \
	} \

#define _array(any) ((ObinArray*) OAny_toCell(any))
#define _array_size(any) ((_array(any))->size)
#define _array_capacity(any) ((_array(any))->capacity)
#define _array_data(any) ((_array(any))->data)
#define _array_item(any, index) ((_array_data(any))[index])
#define _array_setitem(any, index, item) ((_array_data(any))[index] = item)

#define _array_last_index(any) (_array_size(any) - 1)
static obin_bool
_array_grow(ObinState* state, ObinAny self, obin_index count_elements) {
	/*TODO IT IS DANGEROUS OPERATION NEED SAFE CHECKS*/
	obin_mem_t new_capacity;
    if (_array_capacity(self) > OBIN_MAX_CAPACITY - (OBIN_DEFAULT_ARRAY_SIZE + count_elements)) {
    	new_capacity = OBIN_MAX_CAPACITY;
    } else {
    	new_capacity = _array_capacity(self) + OBIN_DEFAULT_ARRAY_SIZE + count_elements;
    }

	if (new_capacity <= _array_capacity(self)) {
		return OFALSE;
	}

	_array_data(self) = obin_memory_realloc(state, _array_data(self), new_capacity);
	_array_capacity(self) = new_capacity;

	return OTRUE;
}

ObinAny
obin_array_new(ObinState* state, ObinAny size) {
	ObinArray * self; obin_mem_t capacity;
	if(obin_any_is_nil(size)){
		size = obin_integer_new(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!obin_integer_is_fit_to_memsize(size)) {
			obin_raise(state, obin_errors(state)->MemoryError,
				"obin_array_new " __TypeName__ "size not fit to memory", size);
	}

	self = obin_new(state, ObinArray);

	capacity = (obin_mem_t) obin_any_integer(size);
	self->data = obin_malloc_array(state, ObinAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	return obin_cell_new(EOBIN_TYPE_ARRAY, (OCell*)self, &__BEHAVIOR__, obin_cells(state)->__Array__);
}

static obin_mem_t _array_inflate(ObinState* state, ObinAny self, obin_index start, obin_index end) {
	obin_mem_t new_size, old_size;
	obin_mem_t length;

	length = end - start;
	old_size = _array_size(self);
	new_size = old_size + length;

	if (new_size > _array_capacity(self)) {
		if ( !_array_grow(state, self, length) ){
			obin_raise(state, obin_errors(state)->MemoryError,
				"__array_inflate " __TypeName__ "can't grow", obin_integer_new(length));
			return 0;
		}
	}

	obin_memmove(_array_data(self) + length, _array_data(self), old_size * sizeof(ObinAny));
	return new_size;
}

ObinAny obin_array_insert_collection(ObinState* state, ObinAny self, ObinAny collection, ObinAny position) {
	ObinAny item;
	obin_index start, end, new_size, collection_size, i, j;

	_CHECK_SELF_TYPE(state, self, obin_array_insert_collection);

	start = obin_any_integer(position);
	collection_size = obin_any_integer(obin_length(state, collection));
	end = start + collection_size;

	if(start > _array_size(self)) {
		return obin_raise(state, obin_errors(state)->KeyError, "obin_array_insert_collection invalid index", position);
	} else if(start == _array_size(self)) {
		return obin_add(state, self, item);
	}

	new_size = _array_inflate(state, self, start, end);
	if(!new_size) {
		return obin_raise(state, obin_errors(state)->KeyError,
				"obin_array_insert inflate error", position);
	}

	i=start;j=0;
	while(i<end && j<collection_size) {
		_array_setitem(self, i, obin_getitem(state, collection, obin_integer_new(j)));
		++i; ++j;
	}

	_array_size(self) = new_size;

	return obin_integer_new(new_size);
}

ObinAny obin_array_insert(ObinState* state, ObinAny self, ObinAny item, ObinAny position) {
	obin_mem_t new_size;
	obin_mem_t insert_index;

	_CHECK_SELF_TYPE(state, self, obin_array_insert);

	insert_index = obin_any_integer(position);
	if(insert_index > _array_size(self)) {
		return obin_raise(state, obin_errors(state)->KeyError, "obin_array_insert invalid index", position);
	} else if(insert_index == _array_size(self)) {
		return obin_array_push(state, self, item);
	}

	new_size = _array_inflate(state, self, insert_index, insert_index + 1);
	if(!new_size) {
		return obin_raise(state, obin_errors(state)->KeyError,
				"obin_array_insert inflate error", position);
	}

	_array_setitem(self, insert_index, item);

	_array_size(self) = new_size;
	return obin_integer_new(new_size);
}

/*
 * implemented __add__
 * */
/*
MAYBE IMPLEMENT IT IN SOURCE
ObinAny obin_array_merge(ObinState* state, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* state, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* state, ObinAny self);
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/
ObinAny
obin_array_push(ObinState* state, ObinAny self, ObinAny value) {
	obin_mem_t new_size;
	_CHECK_SELF_TYPE(state, self, obin_array_push);

	new_size = _array_size(self) + 1;

	if (new_size > _array_capacity(self)){
		if (!_array_grow(state, self, 1) ){
			obin_raise(state, obin_errors(state)->MemoryError,
				"obin_array_push " __TypeName__ "can't grow", obin_integer_new(new_size));
		}
	}

	_array_setitem(self, _array_size(self), value);

	_array_size(self) = new_size;

	return obin_integer_new(new_size);
}

ObinAny obin_array_lastindexof(ObinState* state, ObinAny self, ObinAny item){
	obin_mem_t i;

	_CHECK_SELF_TYPE(state, self, lastindexof);

	for(i=_array_last_index(self); i>=0; --i) {
		if (obin_any_is_true(obin_equal(state, _array_item(self, i), item))) {
			return obin_integer_new(i);
		}
	}

	return obin_integers(state)->NotFound;
}

ObinAny obin_array_indexof(ObinState* state, ObinAny self, ObinAny item) {
	obin_mem_t i;

	_CHECK_SELF_TYPE(state, self, obin_array_indexof);

	for(i=0; i<_array_size(self); ++i) {
		if (obin_any_is_true(obin_equal(state, _array_item(self, i), item))) {
			return obin_integer_new(i);
		}
	}

	return obin_integers(state)->NotFound;
}

ObinAny obin_array_pop(ObinState* state, ObinAny self) {
    ObinAny item;

	_CHECK_SELF_TYPE(state, self, obin_array_pop);

	if(_array_size(self) == 0) {
			obin_raise(state, obin_errors(state)->IndexError,
				"obin_array_pop " __TypeName__ " empty array", ObinNil);
	}

	item = obin_getitem(state, self, obin_integer_new(_array_last_index(self)));
	_array_size(self) -= 1;

	return item;
}

ObinAny obin_array_clear(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, obin_array_clear);
	_array_size(self) = 0;
	return ObinNothing;
}

ObinAny obin_array_remove(ObinState* state, ObinAny self, ObinAny item) {
	obin_integer i;
	obin_bool find;
	find = OFALSE;

	_CHECK_SELF_TYPE(state, self, obin_array_remove);

	for (i=0; i<_array_size(self); i++) {
		if(obin_any_is_true(obin_equal(state, self, item))) {
			find = OTRUE;
			break;
		}
	}

	if(!find) {
		return ObinFalse;
	}

	obin_delitem(state, self, obin_integer_new(i));
	return ObinTrue;
}

/* PRIVATE */

static ObinAny __tobool__(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, __tobool__);
	return obin_bool_new(_array_size(self)>0);
}

static ObinAny __tostring__(ObinState* state, ObinAny self) {
    ObinAny result;

	_CHECK_SELF_TYPE(state, self, __tostring__);
	result = obin_string_join(state, obin_char_new(','), self);
	result = obin_add(state, obin_char_new('['), result);
	result = obin_add(state, result, obin_char_new(']'));

	return result;
}

static void __destroy__(ObinState* state, OCell* self) {
	ObinArray* array = (ObinArray*) self;

	obin_memory_free(state, array->data);
}

static void __mark__(ObinState* state, ObinAny self, obin_func_1 mark) {
	/*TODO each here*/
	obin_index i;

	for(i=0; i<_array_size(self); ++i) {
		mark(state, _array_item(self, i));
	}
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;

	_CHECK_SELF_TYPE(state, self, __clone__);

	result = obin_array_new(state, obin_integer_new(_array_capacity(self)));
	obin_memcpy(_array_data(result), _array_data(self), _array_capacity(self) * sizeof(ObinAny));
	_array_size(result) = _array_size(self);
	return result;
}

static ObinAny __length__(ObinState* state, ObinAny self) {
	_CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_array_size(self));
}

static obin_integer
_get_index(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index;

	if(!obin_any_is_integer(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = obin_any_integer(pos);
	if( index < 0){
		index = _array_size(self) - index;
	} else{
		index = obin_any_integer(pos);
	}

	if (index > _array_size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static ObinAny
__getitem__(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise(state, obin_errors(state)->IndexError,
				__TypeName__ "__getitem__ invalid index", pos);
	}

	return _array_item(self, index);
}

static ObinAny
__setitem__(ObinState* state, ObinAny self, ObinAny pos, ObinAny value){
	obin_integer index;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise(state, obin_errors(state)->IndexError,
				__TypeName__ "__setitem__   invalid index", pos);
	}

	if (_array_size(self) == 0 && index == 0) {
		return obin_array_push(state, self, value);
	}

	_array_setitem(self, index, value);

	return obin_integer_new(index);
}

static ObinAny
__hasitem__(ObinState* state, ObinAny self, ObinAny item){
	return obin_bool_new(obin_any_integer(obin_array_indexof(state, self, item)) != OBIN_INVALID_INDEX);
}

static ObinAny
__delitem__(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index, i;
	obin_mem_t new_size;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise(state, obin_errors(state)->IndexError,
				__TypeName__ "__delitem__ invalid index", pos);
	}

	new_size = _array_size(self) - 1;
	for (i = index; i < new_size; i++){
		_array_item(self, i) = _array_item(self, i + 1);
	}
	_array_size(self) = new_size;

	return ObinNothing;
}

obin_bool obin_module_array_init(ObinState* state) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__destroy__ = __destroy__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = obin_collection_compare;
	__BEHAVIOR__.__iterator__ = obin_sequence_iterator_new;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__delitem__ = __delitem__;
	__BEHAVIOR__.__mark__ = __mark__;

	obin_cells(state)->__Array__ = obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, obin_cells(state)->__Cell__);

	return OTRUE;
}
