#include <obin.h>
/* TODO INTERNATION */
#define __TypeName__  "__Tuple__"
#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isTuple(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
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

ObinTuple* _obin_tuple_new(OState* S,  omem_t size) {
	ObinTuple * self;
	omem_t capacity;

	if(!size){
		return NULL;
	}

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return NULL;
	}
	capacity = sizeof(ObinTuple) + sizeof(OAny) * size;
	self = (ObinTuple*) omemory_allocate_cell(S, capacity);
	self->size = size;
	self->data = (opointer)self + sizeof(ObinTuple);

	return self;
}

OAny OTuple_fromArray(OState* S,  OAny size, OAny* items) {
	ObinTuple * self;

	if(!OAny_isInt(size)){
		return oraise(S, oerrors(S)->TypeError,
				"Tuple.new integer size expected", size);
	}

	if(!OInt_isFitToMemsize(size)) {
		return oraise(S, oerrors(S)->TypeError,
				"Tuple.new invalid size", size);
	}

	self = _obin_tuple_new(S , OAny_intVal(size));

	if(items != NULL) {
		omemcpy(self->data, items, OAny_intVal(size));
	}

	return OCell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, ocells(S)->__Tuple__);
}

OAny OTuple(OState* S, omem_t size, ...){
	ObinTuple * self;
	omem_t i;
	OAny item;
    va_list vargs;

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
		return oraise(S, oerrors(S)->TypeError,
				"Tuple.pack invalid size", OInteger(size));
	}

	self = _obin_tuple_new(S , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
    	item = va_arg(vargs, OAny);
    	self->data[i] = item;
    }
    va_end(vargs);

	return OCell_new(EOBIN_TYPE_TUPLE, (OCell*) self, &__BEHAVIOR__, ocells(S)->__Tuple__);
}

/****************************************  TYPETRAIT  *************************************************/
static OAny __tobool__(OState* S, OAny self) {
    _CHECK_SELF_TYPE(S, self, __tobool__);

	return OBool(_size(self) > 0);
}

static OAny __tostring__(OState* S, OAny self) {
    OAny result;

    _CHECK_SELF_TYPE(S, self, __tostring__);

	result = OString_join(S, OString(S, ","), self);
	result = oadd(S, OString(S, "("), result);
	result = oadd(S, result, OString(S, ",)"));

	return result;
}

static OAny __clone__(OState* S, OAny self) {
	OAny result;

    _CHECK_SELF_TYPE(S, self, __clone__);

	result = OTuple_fromArray(S,  OInteger(_size(self)), _data(self));
	return result;
}

static void __mark__(OState* S, OAny self, ofunc_1 mark) {
	oindex_t i;

	for(i=0; i<_size(self); ++i) {
		mark(S, _get(self, i));
	}
}

static OAny __iterator__(OState* S, OAny self) {
    _CHECK_SELF_TYPE(S, self, __iterator__);

	return OSequence_iterator(S, self);
}

static OAny __length__(OState* S, OAny self) {
    _CHECK_SELF_TYPE(S, self, __length__);

	return OInteger(_size(self));
}

static oint
_get_index(OState* S, OAny self, OAny pos){
	oint index;

	if(!OAny_isInt(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = OAny_intVal(pos);
	if( index < 0){
		index = _size(self) - index;
	} else{
		index = OAny_intVal(pos);
	}

	if (index > _size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static OAny
__getitem__(OState* S, OAny self, OAny pos){
	oint index;

    _CHECK_SELF_TYPE(S, self, __getitem__);

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				"Tuple.__getitem__ invalid index", pos);
	}

	return _get(self, index);
}

static OAny
__hasitem__(OState* S, OAny self, OAny item){
    _CHECK_SELF_TYPE(S, self, __hasitem__);
	return OBool(_get_index(S, self, item) != OBIN_INVALID_INDEX);
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
__hash__(OState* S, OAny self){
    oint mult = 1000003L, x = 0x345678L, y;
    omem_t length = _size(self);
    OAny * items = _data(self);

    while (--length >= 0) {
    	y = OAny_intVal(ohash(S, *items));
    	items++;

        if (y == -1)
            return OInteger(-1);
        x = (x ^ y) * mult;
        /* the cast might truncate len; that doesn't change hash stability */
        mult += (oint)(82520L + length + length);
    }

    x += 97531L;

    if (x == -1) {
        x = -2;
    }

    return OInteger(x);
}


obool otuple_init(OState* S) {
	__BEHAVIOR__.__name__ = __TypeName__;

	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = OCollection_compare;
	__BEHAVIOR__.__hash__ = __hash__;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;

	ocells(S)->__Tuple__ = OCell_new(EOBIN_TYPE_CELL,
			obin_new(S, OCell), &__BEHAVIOR__, ocells(S)->__Cell__);

	return OTRUE;

}
