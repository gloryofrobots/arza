#include <stdarg.h>

#include <core/orandom.h>
#include <core/ocontext.h>
#include <core/omemory.h>
#include <core/obuiltin.h>

#include <types/oerror.h>

#define obin_array_new_default obin_create_array(OBIN_DEFAULT_ARRAY_SIZE)

#define OBIN_ARRAY_MAX_CAPACITY OBIN_MEM_MAX - 1

typedef struct {
	OBIN_CELL_HEADER;

	obin_mem_t size;
	obin_mem_t capacity;

	ObinAny* data;
} ObinArray;

#define _array(any) ((ObinArray*) (any.data.cell))
#define _array_size(any) ((_array(any))->size)
#define _array_capacity(any) ((_array(array))->capacity)
#define _array_data(any) ((_array(any))->data)
#define _array_item(any, index) ((_array_data(any))[index])
#define _array_last_index(any) (_array_size(any) - 1)
/* TRAIT */
/* DO it with map */
static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinAny result;
	ObinAny iterator;
	ObinAny item;
	obin_integer size;

	size =_array_size(self) + 2;
	result = obin_array_new(state, size);
	obin_setitem(result, obin_string_new(state, "["));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}

		obin_setitem(result, obin_tostring(state, item));
	}

	obin_destroy(iterator);
	obin_setitem(result, obin_string_new(state, "]"));
	return obin_string_join(state, obin_string_new(state, ","), result);
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

static ObinNativeTraits __TRAITS__ = {
    &__tostring__,
    &__destroy__,
	&__clone__,
	&obin_collection_compare,
	0, /*__hash__*/

	 __iterator__,
	 __next__,
	 __length__,
	 __getitem__,
	 __setitem__,
	 __hasitem__,

	 0, /*__next__*/
};

ObinAny
array_trait__item__(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index;

	if (!obin_any_is_array(self)){
		return obin_raise_type_error(state, "Array.__item__  invalid call", self);
	}

	if(!obin_any_is_integer(pos)){
		return obin_raise_type_error(state, "Array.__item__ index must be integer", pos);
	}

	index = obin_any_integer(pos);
	if( index < 0){
		index = _array_size(self) - index;
	} else{
		index = obin_any_integer(pos);
	}

	if (index > _array_size(self) || index < 0) {
		return obin_raise_index_error(state, "Array.__item__ invalid index ", pos);
	}

	return _array_item(self, index);
}

static ObinAny
array_trait__length__(ObinState* state, ObinAny self) {
	if (!obin_any_is_array(self)){
		return obin_raise_type_error(state, "Array.__length__  invalid call", self);
	}

	return obin_integer_new(_array_size(self));
}

/* PUBLIC */
ObinAny
obin_array_new(ObinState* state, ObinAny size) {
	ObinArray * self;
	obin_mem_t capacity;
	if(obin_any_is_nil(size)){
		size = obin_integer_new(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!obin_is_number_fit_to_memsize(size)) {
		return obin_raise_memory_error(state, "obin_array_new:: size not fit to memory", size );
	}

	self = obin_malloc_type(state, ObinArray);

	capacity = (obin_mem_t) obin_any_number(size);
	self->data = obin_malloc_collection(state, ObinAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	return obin_cell_new(EOBIN_TYPE_ARRAY, self);
}



ObinAny
obin_array_set(ObinState* state, ObinAny array, const ObinAny index, const ObinAny value) {
	ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;

	if (self->size == 0 && index == 0) {
		//CHECK ERROR
		obin_array_append(self, value);

		return ObinNothing;
	}


	if (index > (self->size - 1)) {
		//TODO
		return NULL;
	}

	self->data[index] = value;

	return ObinNothing;
}

//MUST RETURN INDEX REALLY, DO SOMETHING FOR CACHING INTEGERS
ObinAny
obin_array_add(ObinState* state, ObinAny array, ObinAny value) {
	ObinArray* self;
	obin_mem_t new_size;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	new_size = self->size + 1;

	if (new_size > self->capacity){
		if (!OBIN_IS_SUCCESS(array_grow(self))){
			//TODO ERROR
			return NULL;
		}
	}

	self->data[self->size] = value;
	self->size = new_size;

	return ObinNothing;
}

//MUST RETURN INDEX REALLY, DO SOMETHING FOR CACHING INTEGERS
ObinAny
obin_array_insert(ObinState* state, ObinAny array, ObinAny index, ObinAny value) {
	ObinArray* self;
	obin_mem_t new_size;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	new_size = self->size + 1;

	if (new_size > self->capacity){
		if (!obin_any_is_success(_array_grow(self))){
			//TODO ERROR
			return NULL;
		}
	}

	self->data[self->size] = value;
	self->size = new_size;

	return ObinNothing;
}
ObinAny
obin_array_has_item(ObinState* state, ObinAny array, ObinAny item) {
	obin_mem_t i;
	obin_mem_t new_size;
	ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	for( i=0; i<self->size; ++i) {
		if(self->data[i] == item) {
			return ObinTrue;
		}
	}

	return ObinFalse;
}

ObinAny obin_array_item_index(ObinState* state, ObinAny array, ObinAny item) {
	obin_mem_t i;
    ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;

	for( i=0; i<self->size; ++i) {
		if(self->data[i] == item) {
			return i;
		}
	}

	return -1;
}


ObinAny obin_array_pop(ObinState* state, ObinAny array) {
    ObinArray* self;
    ObinAny item = NULL;
	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	if(self->size == 0) {
		//TODO ERROR
		return NULL;
	}

	item = obin_array_get(array, _array_last_index(self));
	self->size -= 1;

	return ObinNothing;
}


ObinAny obin_array_clear(ObinState* state, ObinAny array) {
    ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	self->size = 0;

	return ObinNothing;
}

/* PRIVATE */
static ObinAny
_array_grow(ObinState* state, ObinArray* self) {
	obin_mem_t new_capacity;
    if (self->capacity > OBIN_ARRAY_MAX_CAPACITY - OBIN_DEFAULT_ARRAY_SIZE) {
    	//TODO DETAILED EXPR
    	new_capacity = OBIN_ARRAY_MAX_CAPACITY;
    }

	new_capacity = self->capacity + OBIN_DEFAULT_ARRAY_SIZE;
	return _array_growto(state, self, new_capacity);
}


static ObinAny
_array_growto(ObinState* state, ObinArray* self, obin_mem_t new_capacity) {
	if (new_capacity <= self->capacity) {
		return ObinFailure;
	}

	ObinAny* new_data;
	obin_realloc(self->data, new_capacity);
	self->capacity = new_capacity;
	return ObinSuccess;
}



//list.extend(L)
//
//    Extend the list by appending all the items in the given list; equivalent to a[len(a):] = L.
//
//list.remove(x)
//
//	Remove the first item from the list whose value is x.and return it //otherwise NOValuej

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
