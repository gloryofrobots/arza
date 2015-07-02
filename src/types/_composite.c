#include <core/obin.h>

typedef struct {
	OBIN_CELL_HEADER;
	/*array of traits */
	ObinAny traits;
	ObinAny scope;
} ObinCompositeCell;


#define _composite(any) ((ObinCompositeCell*) (any.data.cell))
#define _traits(any) ((_composite(any))->traits)
#define _scope(any) ((_composite(any))->scope)

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinCompositeCell* cell;

	cell = _composite(self);

	return obin_string_pack(state, 2,
				OSTR(state, "<Cell"),
				obin_hex(state, OINT((int)cell)),
				OSTR(state,">")
	);
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

static ObinNativeTraits __TRAITS__ = {
    &__tostring__,
    &__destroy__,
	&__clone__,
	&obin_collection_compare,
	__hash__,

	 __iterator__,
	 __length__,
	 __getitem__,
	 0 ,/*__setitem__,*/
	 __hasitem__,
	 0, /*__delitem__,*/

	 0, /*__next__*/
};

static ObinTuple*
_obin_tuple_new(ObinState* state, obin_mem_t size) {
	ObinTuple * self;
	self = obin_malloc_type(state, ObinTuple);
	self->size = size;
	self->native_traits = &__TRAITS__;
	self->data = obin_malloc_collection(state, ObinAny, size);
	return self;
}

