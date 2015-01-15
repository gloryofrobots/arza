#include "ointernal_types.h"

#define obin_create_array_default obin_create_array(OBIN_DEFAULT_ARRAY_SIZE)

#define obin_array_check(array) ( array->type == EOBIN_TYPE_ARRAY )

#define OBIN_ARRAY_MAX_CAPACITY OBIN_MEM_MAX - 1

#define _array_last_index(array) (array->size - 1)

//TODO ERROR NULL IS NOT GOOD HERE
#define _CHECK_ARRAY_TYPE(array) \
	if(! obin_array_check(array)) { \
		return NULL; \
	}

typedef struct _ObinArray {
	ObinCellGCHead
	obin_mem_t size;
	ObinCell** data;

	obin_mem_t capacity;
} ObinArray;

typedef void (* ObinArrayForeach) (ObinCell* item, obin_pointer arg);

ObinCell *
obin_create_array(int size) {
	ObinArray * self;

	self = (ObinArray*) obin_gc_new(ObinArray, EOBIN_TYPE_ARRAY);
	self.data = obin_malloc(sizeof(obin_mem_t)*size);
	self->capacity = size;
	self->size = 0;
	return self;
}


ObinCell*
obin_array_get(ObinCell* array, obin_mem_t index){
	ObinArray* self;
	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	if (index > self->size) {
		//TODO ERROR HERE
		return NULL;
	}

	return self->data[index];
}

obin_mem_t obin_array_size(ObinCell* array) {
	return ((ObinArray*) array)->size;
}


ObinCell*
obin_array_set(ObinCell* array, obin_mem_t index, ObinCell* value) {
	ObinArray* self;

	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;

	if (self->size == 0 && index == 0) {
		//CHECK ERROR
		obin_array_append(self, value);
		return ObinNoValue;
	}

	if (index > (self->size - 1)) {
		//TODO
		return NULL;
	}

	self->data[index] = value;
	return ObinNoValue;
}

//MUST RETURN INDEX REALLY, DO SOMETHING FOR CACHING INTEGERS
ObinCell* obin_array_append(ObinCell* array, ObinCell* value) {
	ObinArray* self;
	obin_mem_t new_size;

	_CHECK_ARRAY_TYPE(array);

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

	return ObinNoValue;
}


EOBIN_RESULT _array_grow(ObinArray* self) {
	obin_mem_t new_capacity;
    if (self->capacity > OBIN_ARRAY_MAX_CAPACITY - OBIN_DEFAULT_ARRAY_SIZE) {
    	//TODO DETAILED EXPR
    	new_capacity = OBIN_ARRAY_MAX_CAPACITY;
    }

	new_capacity = self->capacity + OBIN_DEFAULT_ARRAY_SIZE;
	return _array_growto(self, new_capacity);
}

EOBIN_RESULT _array_growto(ObinArray* self, obin_mem_t new_capacity) {
	if (new_capacity <= self->capacity) {
		return EOBIN_INTERNAL_ERROR;
	}

	ObinCell** new_data;
	obin_realloc(self->data, new_capacity);
	self->capacity = new_capacity;
	return EOBIN_SUCCESS;
}


ObinCell* obin_array_has_item(ObinCell* array, ObinCell* item) {
	obin_mem_t i;
	obin_mem_t new_size;
	ObinArray* self;

	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	for( i=0; i<self->size; ++i) {
		if(self->data[i] == item) {
			return ObinTrue;
		}
	}

	return ObinFalse;
}

ObinCell* obin_array_item_index(ObinCell * array, ObinCell* item) {
	obin_mem_t i;
    ObinArray* self;

	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;

	for( i=0; i<self->size; ++i) {
		if(self->data[i] == item) {
			return i;
		}
	}

	return -1;
}


ObinCell* obin_array_pop(ObinCell* array) {
    ObinArray* self;
    ObinCell* item = NULL;
	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	if(self->size == 0) {
		//TODO ERROR
		return NULL;
	}

	item = obin_array_get(array, _array_last_index(self));
	self->size -= 1;

	OBIN_END_PROC;
}

ObinCell* obin_array_clear(ObinCell* array) {
    ObinArray* self;

	_CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	self->size = 0;

	OBIN_END_PROC;
}

ObinCell* obin_array_to_string(ObinCell* array) {
	//TODO IMPLEMENT
	return NULL;
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
