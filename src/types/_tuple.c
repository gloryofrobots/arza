#include <stdarg.h>
#include <core/orandom.h>
#include <core/obin.h>
/* TODO INTERNATION */

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t size;
	ObinAny* data;
} ObinTuple;

#define _tuple(any) ((ObinTuple*) (any.data.cell))
#define _size(any) ((_tuple(any))->size)
#define _data(any) ((_tuple(any))->data)
#define _get(any, index) ((_data(any))[index])

static ObinNativeTraits __TRAITS__;

static ObinTuple*
_obin_tuple_new(ObinState* state, obin_mem_t size) {
	ObinTuple * self;
	self = obin_malloc_type(state, ObinTuple);
	self->size = size;
	self->native_traits = &__TRAITS__;
	self->data = obin_malloc_collection(state, ObinAny, size);
	return self;
}

ObinAny obin_tuple_new(ObinState* state, ObinAny* items, ObinAny size) {
	ObinTuple * self;
	obin_mem_t capacity;

	if(!obin_any_is_integer(size)){
		return obin_raise_memory_error(state, "Tuple.new -> integer size expected", size );
	}

	if(!obin_integer_is_fit_to_memsize(size)) {
		return obin_raise_memory_error(state, "Tuple.new -> invalid size", size );
	}

	capacity = (obin_mem_t) obin_any_integer(size);
	self = _obin_tuple_new(state , capacity);
	obin_memcpy(self->data, items, capacity);

	return obin_cell_new(EOBIN_TYPE_TUPLE, (ObinCell*) self);
}

ObinAny obin_tuple_pack(ObinState* state, obin_mem_t size, ...){
	ObinTuple * self;
	obin_mem_t i;
	ObinAny item;
    va_list vargs;

	if(!obin_is_fit_to_memsize(size)) {
		return obin_raise_memory_error(state, "Tuple.new -> invalid size", obin_integer_new(size));
	}

	self = _obin_tuple_new(state , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
    	item = va_arg(vargs, ObinAny);
    	self->data[i] = item;
    }
    va_end(vargs);

	return obin_cell_new(EOBIN_TYPE_TUPLE, (ObinCell*) self);
}


/****************************************  TYPETRAIT  *************************************************/

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinAny array;
	ObinAny iterator;
	ObinAny item;
	obin_integer size;
    ObinAny result;

	size =_size(self) + 2;
	array = obin_array_new(state, obin_integer_new(size));

	iterator = obin_iterator(state, self);

	while (OTRUE) {
		item = obin_next(state, iterator);
		if (obin_is_stop_iteration(item)) {
			break;
		}

		obin_array_append(state, array, obin_tostring(state, item));
	}

	result = obin_string_join(state, obin_char_new(state, ','), array);
	result = obin_string_concat(state, obin_char_new(state, '['), result);
	result = obin_string_concat(state, result, obin_char_new(state, ']'));

	return result;
}

static ObinAny __destroy__(ObinState* state, ObinAny self) {
	obin_free(_data(self));
	obin_free(obin_any_cell(self));
	return ObinNothing;
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;
	result = obin_tuple_new(state, _data(self), _size(self));
	return result;
}

static ObinAny __iterator__(ObinState* state, ObinAny self) {
	return obin_sequence_iterator_new(state, self);
}

static ObinAny __length__(ObinState* state, ObinAny self) {
	return obin_integer_new(_size(self));
}

static obin_integer
_get_index(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index;

	if(!obin_any_is_integer(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = obin_any_integer(pos);
	if( index < 0){
		index = _size(self) - index;
	} else{
		index = obin_any_integer(pos);
	}

	if (index > _size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static ObinAny
__getitem__(ObinState* state, ObinAny self, ObinAny pos){
	obin_integer index;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise_index_error(state, "Tuple.__getitem__ invalid index ", pos);
	}

	return _get(self, index);
}

static ObinAny
__hasitem__(ObinState* state, ObinAny self, ObinAny item){
	return obin_bool_new(obin_any_integer(obin_array_indexof(state, self, item)) != OBIN_INVALID_INDEX);
}

/*
 * Stolen from Python
 * The addend 82520, was selected from the range(0, 1000000) for
   generating the greatest number of prime multipliers for tuples
   upto length eight:

     1082527, 1165049, 1082531, 1165057, 1247581, 1330103, 1082533,
     1330111, 1412633, 1165069, 1247599, 1495177, 1577699
*/

static ObinAny
__hash__(ObinState* state, ObinAny self){
    obin_integer mult = 1000003L, x = 0x345678L, y;
    obin_mem_t length = _size(self);
    ObinAny * items = _data(self);

    while (--length >= 0) {
    	y = obin_hash(state, *items);
    	items++;

        if (y == -1)
            return obin_integer_new(-1);
        x = (x ^ y) * mult;
        /* the cast might truncate len; that doesn't change hash stability */
        mult += (obin_integer)(82520L + length + length);
    }

    x += 97531L;

    if (x == -1) {
        x = -2;
    }

    return obin_integer_new(x);
}

ObinCollectionTrait __COLLECTION__ = {
	 __iterator__,
	 __length__,
	 __getitem__,
	 0 ,/*__setitem__,*/
	 __hasitem__,
	 0, /*__delitem__,*/
} ;

static ObinNativeTraits __TRAITS__ = {
	"__tuple",
    &__tostring__,
    &__destroy__,
	&__clone__,
	&obin_collection_compare,
	__hash__,

	&__COLLECTION__,

	 0, /* iterator */
	 0, /* number */
};
