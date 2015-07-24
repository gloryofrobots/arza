#include <obin.h>
/* TODO INTERNATION */
#define __TypeName__  "__Tuple__"
#define _CHECK_SELF_TYPE(state, self, method) \
	if(!OAny_isTuple(self)) { \
		return oraise(state, oerrors(state)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

typedef struct {
	OCELL_HEADER;
	omem_t size;
	OAny* data;
} ObinTuple;

#define _tuple(any) ((ObinTuple*) (any.data.cell))
#define _size(any) ((_tuple(any))->size)
#define _data(any) ((_tuple(any))->data)
#define _get(any, index) ((_data(any))[index])

static OBehavior __BEHAVIOR__ = {0};

ObinTuple* _obin_tuple_new(OState* state,  omem_t size) {
	ObinTuple * self;
	omem_t capacity;

	if(!size){
		return NULL;
	}

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return NULL;
	}
	capacity = sizeof(ObinTuple) + sizeof(OAny) * size;
	self = (ObinTuple*) obin_allocate_cell(state, capacity);
	self->size = size;
	self->data = (opointer)self + sizeof(ObinTuple);

	return self;
}

OAny obin_tuple_new(OState* state,  OAny size, OAny* items) {
	ObinTuple * self;

	if(!OAny_isInt(size)){
		return oraise(state, oerrors(state)->TypeError,
				"Tuple.new integer size expected", size);
	}

	if(!OInt_isFitToMemsize(size)) {
		return oraise(state, oerrors(state)->TypeError,
				"Tuple.new invalid size", size);
	}

	self = _obin_tuple_new(state , OAny_toInt(size));

	if(items != NULL) {
		omemcpy(self->data, items, OAny_toInt(size));
	}

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, ocells(state)->__Tuple__);
}

OAny obin_tuple_pack(OState* state, omem_t size, ...){
	ObinTuple * self;
	omem_t i;
	OAny item;
    va_list vargs;

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return oraise(state, oerrors(state)->TypeError,
				"Tuple.pack invalid size", obin_integer_new(size));
	}

	self = _obin_tuple_new(state , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
    	item = va_arg(vargs, OAny);
    	self->data[i] = item;
    }
    va_end(vargs);

	return obin_cell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, ocells(state)->__Tuple__);
}

/****************************************  TYPETRAIT  *************************************************/
static OAny __tobool__(OState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __tobool__);

	return obin_bool_new(_size(self) > 0);
}

static OAny __tostring__(OState* state, OAny self) {
    OAny result;

    _CHECK_SELF_TYPE(state, self, __tostring__);

	result = obin_string_join(state, obin_char_new(','), self);
	result = obin_add(state, obin_char_new('('), result);
	result = obin_add(state, result, obin_string_new(state, ",)"));

	return result;
}

static OAny __clone__(OState* state, OAny self) {
	OAny result;

    _CHECK_SELF_TYPE(state, self, __clone__);

	result = obin_tuple_new(state,  obin_integer_new(_size(self)), _data(self));
	return result;
}

static void __mark__(OState* state, OAny self, ofunc_1 mark) {
	oindex_t i;

	for(i=0; i<_size(self); ++i) {
		mark(state, _get(self, i));
	}
}

static OAny __iterator__(OState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __iterator__);

	return obin_sequence_iterator_new(state, self);
}

static OAny __length__(OState* state, OAny self) {
    _CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_size(self));
}

static oint
_get_index(OState* state, OAny self, OAny pos){
	oint index;

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
__getitem__(OState* state, OAny self, OAny pos){
	oint index;

    _CHECK_SELF_TYPE(state, self, __getitem__);

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(state, oerrors(state)->IndexError,
				"Tuple.__getitem__ invalid index", pos);
	}

	return _get(self, index);
}

static OAny
__hasitem__(OState* state, OAny self, OAny item){
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
__hash__(OState* state, OAny self){
    oint mult = 1000003L, x = 0x345678L, y;
    omem_t length = _size(self);
    OAny * items = _data(self);

    while (--length >= 0) {
    	y = OAny_toInt(obin_hash(state, *items));
    	items++;

        if (y == -1)
            return obin_integer_new(-1);
        x = (x ^ y) * mult;
        /* the cast might truncate len; that doesn't change hash stability */
        mult += (oint)(82520L + length + length);
    }

    x += 97531L;

    if (x == -1) {
        x = -2;
    }

    return obin_integer_new(x);
}


obool obin_module_tuple_init(OState* state) {
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

	ocells(state)->__Tuple__ = obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, ocells(state)->__Cell__);

	return OTRUE;

}
