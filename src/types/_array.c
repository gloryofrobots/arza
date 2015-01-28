#include "../obuiltin.h"

#define obin_array_new_default obin_create_array(OBIN_DEFAULT_ARRAY_SIZE)

#define OBIN_ARRAY_MAX_CAPACITY OBIN_MEM_MAX - 1

#define _array_last_index(array) (array->size - 1)

#define CHECK_ARRAY_TYPE(array) OBIN_ANY_CHECK_TYPE(array, EOBIN_TYPE_ARRAY)


typedef struct {
	OBIN_CELL_HEADER;
	OBIN_DEFINE_TYPE_TRAIT(ObinCollectionTrait);

	obin_mem_t size;
	obin_mem_t capacity;

	ObinAny* data;
} ObinArray;

/* PUBLIC */
ObinAny
obin_array_new(ObinState* state, ObinAny size) {
	ObinArray * self;
	obin_mem_t capacity;
	if (!obin_is_number_fit_to_memsize(size)) {
		return obin_raise(state, ObinInvalidSizeError,
				obin_string_new(state, "obin_array_new:: size not fit to memory"), size);
	}

	self = obin_malloc_type(ObinArray);

	capacity = (obin_mem_t) obin_any_number(size);
	self->data = obin_malloc_collection(ObinAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	return obin_cell_new(EOBIN_TYPE_ARRAY, self);
}

ObinAny
obin_array_get(ObinState* state, ObinAny array, ObinAny index){
	ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) obin_to_cell(array);

	if (index > self->size) {
		//TODO ERROR HERE
		return NULL;
	}

	return self->data[index];
}

ObinAny
obin_array_size(ObinState* state, const ObinAny array) {
	ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) obin_to_cell(array);

	return obin_integer_new(self->size);
}


ObinAny
obin_array_set(ObinState* state, ObinAny array, const ObinAny index, const ObinAny value) {
	ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;

	if (self->size == 0 && index == 0) {
		//CHECK ERROR
		obin_array_append(self, value);

		OBIN_END_PROC;_
	}


	if (index > (self->size - 1)) {
		//TODO
		return NULL;
	}

	self->data[index] = value;

	OBIN_END_PROC;
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

	return ObinNoValue;
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

	return ObinNoValue;
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

	OBIN_END_PROC;
}


ObinAny obin_array_clear(ObinState* state, ObinAny array) {
    ObinArray* self;

	CHECK_ARRAY_TYPE(array);

	self = (ObinArray*) array;
	self->size = 0;

	OBIN_END_PROC;
}

ObinAny obin_array_to_string(ObinState* state, ObinAny array) {
	//TODO IMPLEMENT
	return NULL;
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
