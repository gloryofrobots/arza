#include <obin.h>
/* TODO INTERNATION */
#define __TypeName__  "__Tuple__"
#define _CHECK_SELF_TYPE(state, self, method) \
	if(!obin_any_is_tuple(self)) { \
		return obin_raise(state, obin_errors(state)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t size;
	ObinAny* data;
} ObinTuple;

#define _tuple(any) ((ObinTuple*) (any.data.cell))
#define _size(any) ((_tuple(any))->size)
#define _data(any) ((_tuple(any))->data)
#define _get(any, index) ((_data(any))[index])

static ObinBehavior __BEHAVIOR__ = {0};

ObinTuple* _obin_tuple_new(ObinState* state,  obin_mem_t size) {
	ObinTuple * self;
	obin_mem_t capacity;

	if(!size){
		return NULL;
	}

	if(!obin_is_fit_to_memsize(size)) {
		return NULL;
	}
	capacity = sizeof(ObinTuple) + sizeof(ObinAny) * size;
	self = (ObinTuple*) obin_allocate_cell(state, capacity);
	self->size = size;
	self->data = (obin_pointer)self + sizeof(ObinTuple);

	return self;
}

ObinAny obin_tuple_new(ObinState* state,  ObinAny size, ObinAny* items) {
	ObinTuple * self;

	if(!obin_any_is_integer(size)){
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.new integer size expected", size);
	}

	if(!obin_integer_is_fit_to_memsize(size)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.new invalid size", size);
	}

	self = _obin_tuple_new(state , obin_any_integer(size));

	if(items != NULL) {
		obin_memcpy(self->data, items, obin_any_integer(size));
	}

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, obin_cells(state)->__Tuple__);
}

ObinAny obin_tuple_pack(ObinState* state, obin_mem_t size, ...){
	ObinTuple * self;
	obin_mem_t i;
	ObinAny item;
    va_list vargs;

	if(!obin_is_fit_to_memsize(size)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.pack invalid size", obin_integer_new(size));
	}

	self = _obin_tuple_new(state , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
    	item = va_arg(vargs, ObinAny);
    	self->data[i] = item;
    }
    va_end(vargs);

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, obin_cells(state)->__Tuple__);
}

/****************************************  TYPETRAIT  *************************************************/
static ObinAny __tobool__(ObinState* state, ObinAny self) {
    _CHECK_SELF_TYPE(state, self, __tobool__);

	return obin_bool_new(_size(self) > 0);
}

static ObinAny __tostring__(ObinState* state, ObinAny self) {
    ObinAny result;

    _CHECK_SELF_TYPE(state, self, __tostring__);

	result = obin_string_join(state, obin_char_new(','), self);
	result = obin_add(state, obin_char_new('('), result);
	result = obin_add(state, result, obin_string_new(state, ",)"));

	return result;
}

static ObinAny __clone__(ObinState* state, ObinAny self) {
	ObinAny result;

    _CHECK_SELF_TYPE(state, self, __clone__);

	result = obin_tuple_new(state,  obin_integer_new(_size(self)), _data(self));
	return result;
}

static void __mark__(ObinState* state, ObinAny self, obin_func_1 mark) {
	obin_index i;

	for(i=0; i<_size(self); ++i) {
		mark(state, _get(self, i));
	}
}

static ObinAny __iterator__(ObinState* state, ObinAny self) {
    _CHECK_SELF_TYPE(state, self, __iterator__);

	return obin_sequence_iterator_new(state, self);
}

static ObinAny __length__(ObinState* state, ObinAny self) {
    _CHECK_SELF_TYPE(state, self, __length__);

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

    _CHECK_SELF_TYPE(state, self, __getitem__);

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise(state, obin_errors(state)->IndexError,
				"Tuple.__getitem__ invalid index", pos);
	}

	return _get(self, index);
}

static ObinAny
__hasitem__(ObinState* state, ObinAny self, ObinAny item){
    _CHECK_SELF_TYPE(state, self, __hasitem__);
	return obin_bool_new(_get_index(state, self, item) != OBIN_INVALID_INDEX);
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
    	y = obin_any_integer(obin_hash(state, *items));
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


obin_bool obin_module_tuple_init(ObinState* state) {
	__BEHAVIOR__.__name__ = __TypeName__;

	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = obin_collection_compare;
	__BEHAVIOR__.__hash__ = __hash__;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;

	obin_cells(state)->__Tuple__ = obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, obin_cells(state)->__Cell__);

	return OTRUE;

}
