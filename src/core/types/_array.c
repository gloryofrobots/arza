#include <obin.h>

typedef struct {
	OBIN_CELL_HEADER;

	obin_mem_t size;
	obin_mem_t capacity;

	ObinAny* data;
} ObinArray;

#define _array(any) ((ObinArray*) (any.data.cell))
#define _array_size(any) ((_array(any))->size)
#define _array_capacity(any) ((_array(any))->capacity)
#define _array_data(any) ((_array(any))->data)
#define _array_item(any, index) ((_array_data(any))[index])
#define _array_setitem(any, index, item) ((_array_data(any))[index] = item)

#define _array_last_index(any) (_array_size(any) - 1)
/* TRAIT */
static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinAny array;
	ObinAny iterator;
	ObinAny item;
	obin_integer size;
    ObinAny result;

	size =_array_size(self) + 2;
	array = obin_array_new(state, size);

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}

		obin_array_append(state, array, obin_tostring(state, item));
	}

	result = obin_string_join(state, obin_char_new(state, ','), result);
	result = obin_string_concat(state, obin_char_new(state, '['), result);
	result = obin_string_concat(state, result, obin_char_new(state, ']'));

	return result;
}

static ObinAny __destroy__(ObinState* state, ObinAny self) {
	obin_free(_array_data(self));
	obin_free(obin_any_cell(self));
	return ObinNothing;
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;
	ObinAny iterator;
	ObinAny item;

	result = obin_array_new(state, _array_capacity(self));
	obin_memcpy(_array_data(result), _array_data(self), _array_capacity(self) * sizeof(ObinAny));
	_array_size(result) = _array_size(self);
	return result;
}

static ObinAny __iterator__(ObinState* state, ObinAny self) {
	return obin_sequence_iterator_new(state, self);
}

static ObinAny __length__(ObinState* state, ObinAny self) {
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
		return obin_raise_index_error(state, "Array.__getitem__ invalid index ", pos);
	}

	return _array_item(self, index);
}

static ObinAny
__setitem__(ObinState* state, ObinAny self, ObinAny key, ObinAny value){
	obin_integer index;

	index = _get_index(state, self, key);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise_index_error(state, "Array.__setitem__ invalid index ", key);
	}

	if (_array_size(self) == 0 && index == 0) {
		return obin_array_append(state, self, value);
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
		return obin_raise_index_error(state, "Array.__delitem__ invalid index ", pos);
	}

	new_size = _array_size(self) - 1;
	for (i = index; i < new_size; i++){
		_array_item(self, i) = _array_item(self, i + 1);
	}
	_array_size(self) = new_size;

	return ObinNothing;
}

static ObinNativeTraits __TRAITS__ = {
    &__tostring__,
    &__destroy__,
	&__clone__,
	&obin_collection_compare,
	0, /*__hash__*/

	 __iterator__,
	 __length__,
	 __getitem__,
	 __setitem__,
	 __hasitem__,
	 __delitem__,

	 0, /*__next__*/
};

/* PUBLIC */
ObinAny
obin_array_new(ObinState* state, ObinAny size) {
	ObinArray * self; obin_mem_t capacity;
	if(obin_any_is_nil(size)){
		size = obin_integer_new(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!obin_integer_is_fit_to_memsize(size)) {
		return obin_raise_memory_error(state, "obin_array_new:: size not fit to memory", size );
	}

	self = obin_malloc_type(state, ObinArray);

	capacity = (obin_mem_t) obin_any_number(size);
	self->data = obin_malloc_array(state, ObinAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	self->native_traits = &__TRAITS__;
	return obin_cell_new(EOBIN_TYPE_ARRAY, self);
}

ObinAny obin_array_indexof(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_lastindexof(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_pop(ObinState* state, ObinAny self);
ObinAny obin_array_clear(ObinState* state, ObinAny self);
ObinAny obin_array_removeitem(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_removeat(ObinState* state, ObinAny self, ObinAny position);
ObinAny obin_array_insert(ObinState* state, ObinAny self, ObinAny item, ObinAny position);
ObinAny obin_array_merge(ObinState* state, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* state, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* state, ObinAny self);
/*
 * implemented __add__
 * */
/*
MAYBE IMPLEMENT IT IN SOURCE
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
	if(!obin_any_is_array(self)){
		return obin_raise_type_error(state, "Array.append invalid call", self);
	}

	new_size = _array_size(self) + 1;

	if (new_size > _array_capacity(self)){
		if ( !obin_any_is_true(_array_grow(self)) ){
			return obin_raise_memory_error(state, "Array.append error while growing", self);
		}
	}

	_array_setitem(self, _array_size(self), value);

	_array_size(self) = new_size;

	return obin_integer_new(new_size);
}

ObinAny obin_array_indexof(ObinState* state, ObinAny self, ObinAny item) {
	obin_mem_t i;

	if(!obin_any_is_array(self)){
		return obin_raise_type_error(state, "Array.indexof invalid call", self);
	}

	for(i=0; i<_array_size(self); ++i) {
		if (obin_any_is_true(obin_equal(state, _array_item(self, i), item))) {
			return obin_integer_new(i);
		}
	}

	return obin_integer_new(OBIN_INVALID_INDEX);
}

ObinAny obin_array_pop(ObinState* state, ObinAny self) {
    ObinAny item = NULL;
	if(!obin_any_is_array(self)){
		return obin_raise_type_error(state, "Array.pop invalid call", self);
	}

	if(_array_size(self) == 0) {
		return obin_raise_index_error(state, "Array.pop empty array", self);
	}

	item = obin_getitem(state, self, _array_last_index(self));
	_array_size(self) -= 1;

	return item;
}

ObinAny obin_array_clear(ObinState* state, ObinAny self) {
	_array_size(self) = 0;
	return ObinNothing;
}

ObinAny obin_array_remove(ObinState* state, ObinAny self, ObinAny item) {
	obin_integer i;
	obin_bool find;
	find = OFALSE;

	for (i=0; i<_array_size(self); i++) {
		if(obin_any_is_true(obin_equal(self, item))) {
			find = OTRUE;
			break;
		}
	}

	if(!find) {
		return ObinNothing;
	}

	obin_delitem(state, self, obin_integer_new(i));
	return ObinNothing;
}

/* PRIVATE */
static ObinAny
_array_grow(ObinState* state, ObinAny self) {
	obin_mem_t new_capacity;
    if (_array_capacity(self) > OBIN_MAX_CAPACITY - OBIN_DEFAULT_ARRAY_SIZE) {
    	//TODO DETAILED EXPR
    	new_capacity = OBIN_MAX_CAPACITY;
    } else {
    	new_capacity = _array_capacity(self) + OBIN_DEFAULT_ARRAY_SIZE;
    }

	if (new_capacity <= _array_capacity(self)) {
		return ObinFalse;
	}

	obin_realloc(_array_data(self), new_capacity);
	_array_capacity(self) = new_capacity;

	return ObinTrue;
}


//list.extend(L)
//
//    Extend the list by appending all the items in the given list; equivalent to a[len(a):] = L.
//

//list.count(x)
//
//    Return the number of times x appears in the list.
//
//
//	list.reverse()
//
//	    Reverse the elements of the list, in place.


//    public void foreach(ForeachFunction fn) {
//        int size = size();
//        for (int i = 0; i < size; i++) {
//            if (fn.call(mData[i]) == false) {
//                return;
//            }
//        }
//    }
