#include <obin.h>
/* TODO INTERNATION */
#define __TypeName__  "__Tuple__"
#define _CHECK_SELF_TYPE(state, self, method) \
	if(!OAny_isTuple(self)) { \
		return obin_raise(state, obin_errors(state)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t size;
	OAny* data;
} ObinTuple;

#define _tuple(any) ((ObinTuple*) (any.data.cell))
#define _size(any) ((_tuple(any))->size)
#define _data(any) ((_tuple(any))->data)
#define _get(any, index) ((_data(any))[index])

static OBehavior __BEHAVIOR__ = {0};

ObinTuple* _obin_tuple_new(ObinState* state,  obin_mem_t size) {
	ObinTuple * self;
	obin_mem_t capacity;

	if(!size){
		return NULL;
	}

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return NULL;
	}
	capacity = sizeof(ObinTuple) + sizeof(OAny) * size;
	self = (ObinTuple*) obin_allocate_cell(state, capacity);
	self->size = size;
	self->data = (obin_pointer)self + sizeof(ObinTuple);

	return self;
}

OAny obin_tuple_new(ObinState* state,  OAny size, OAny* items) {
	ObinTuple * self;

	if(!OAny_isInt(size)){
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.new integer size expected", size);
	}

	if(!OInt_isFitToMemsize(size)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.new invalid size", size);
	}

	self = _obin_tuple_new(state , OAny_toInt(size));

	if(items != NULL) {
		obin_memcpy(self->data, items, OAny_toInt(size));
	}

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, obin_cells(state)->__Tuple__);
}

OAny obin_tuple_pack(ObinState* state, obin_mem_t size, ...){
	ObinTuple * self;
	obin_mem_t i;
	OAny item;
    va_list vargs;

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return obin_raise(state, obin_errors(state)->TypeError,
				"Tuple.pack invalid size", obin_integer_new(size));
	}

	self = _obin_tuple_new(state , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
    	item = va_arg(vargs, OAny);
    	self->data[i] = item;
    }
    va_end(vargs);

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, obin_cells(state)->__Tuple__);
}

/****************************************  TYPETRAIT  *************************************************/
static OAny __tobool__(ObinState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __tobool__);

	return obin_bool_new(_size(self) > 0);
}

static OAny __tostring__(ObinState* state, OAny self) {
    OAny result;

    _CHECK_SELF_TYPE(state, self, __tostring__);

	result = obin_string_join(state, obin_char_new(','), self);
	result = obin_add(state, obin_char_new('('), result);
	result = obin_add(state, result, obin_string_new(state, ",)"));

	return result;
}

static OAny __clone__(ObinState* state, OAny self) {
	OAny result;

    _CHECK_SELF_TYPE(state, self, __clone__);

	result = obin_tuple_new(state,  obin_integer_new(_size(self)), _data(self));
	return result;
}

static void __mark__(ObinState* state, OAny self, ofunc_1 mark) {
	obin_index i;

	for(i=0; i<_size(self); ++i) {
		mark(state, _get(self, i));
	}
}

static OAny __iterator__(ObinState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __iterator__);

	return obin_sequence_iterator_new(state, self);
}

static OAny __length__(ObinState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_size(self));
}

static obin_integer
_get_index(ObinState* state, OAny self, OAny pos){
	obin_integer index;

	if(!OAny_isInt(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = OAny_toInt(pos);
	if( index < 0){
		index = _size(self) - index;
	} else{
		index = OAny_toInt(pos);
	}

	if (index > _size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static OAny
__getitem__(ObinState* state, OAny self, OAny pos){
	obin_integer index;

    _CHECK_SELF_TYPE(state, self, __getitem__);

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return obin_raise(state, obin_errors(state)->IndexError,
				"Tuple.__getitem__ invalid index", pos);
	}

	return _get(self, index);
}

static OAny
__hasitem__(ObinState* state, OAny self, OAny item){
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

static OAny
__hash__(ObinState* state, OAny self){
    obin_integer mult = 1000003L, x = 0x345678L, y;
    obin_mem_t length = _size(self);
    OAny * items = _data(self);

    while (--length >= 0) {
    	y = OAny_toInt(obin_hash(state, *items));
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
