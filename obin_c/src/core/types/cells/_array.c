#include <obin.h>
/* TODO INTERNATION */
#define __TypeName__  "__Array__"

#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isArray(self)) { \
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \
	} \

OCELL_DECLARE(ObinArray,
	omem_t size;
	OAny* data;
	oint hash;
);

#define _array(any) ((ObinArray*) (any.data.cell))
#define _size(any) ((_array(any))->size)
#define _data(any) ((_array(any))->data)
#define _hash(any) ((_array(any))->hash)
#define _get(any, index) ((_data(any))[index])
#define _setitem(any, index, item) ((_data(any))[index] = item)

static OBehavior __BEHAVIOR__ = {0};

ObinArray* _obin_array_new(OState* S,  omem_t size) {
	ObinArray * self;
	omem_t capacity;

	capacity = sizeof(ObinArray) + sizeof(OAny) * size;
	self = (ObinArray*) omemory_allocate_cell(S, capacity);
	self->size = size;
	if(self->size) {
		self->data = (opointer)self + sizeof(ObinArray);
	}
	else {
		self->data = 0;
	}

	self->hash = 0;

	return self;
}

#define OArray_make(cell) OCell_new(__OArrayTypeId__, (OCell*) self, &__BEHAVIOR__)

OAny _obin_array_empty(OState* S) {
	ObinArray* self;
	self =  _obin_array_new(S , 0);
	return OArray_make(self);
}

OAny OArray_fromCArray(OState* S,  OAny size, OAny* items) {
	ObinArray * self;

	if(!OAny_isInt(size)){
		return oraise(S, oerrors(S)->TypeError,
				"OArray_fromCArray integer size expected", size);
	}
	if(OAny_intVal(size) == 0) {
		return _obin_array_empty(S);
	}
	if(!OInt_isFitToMemsize(size)) {
		return oraise(S, oerrors(S)->TypeError,
				"OArray_fromCArray invalid size", size);
	}

	self = _obin_array_new(S , OAny_intVal(size));

	if(items != NULL) {
		omemcpy(self->data, items, OAny_intVal(size) * sizeof(OAny));
	}

	return OArray_make(self);
}

OAny OArray(OState* S, omem_t size) {
	ObinArray * self;

	if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
			return oraise(S, oerrors(S)->TypeError,
					"Array invalid size", OInteger(size));
	}

	self = _obin_array_new(S , size);
	return OArray_make(self);
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

	result = OArray_fromCArray(S,  OInteger(_size(self)), _data(self));
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

	if (index >= _size(self) || index < 0) {
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
    oindex_t i;

	for(i=0; i<_size(self); ++i) {
		 if(OAny_isTrue(oequal(S,_get(self, i), item))) {
			 return ObinTrue;
		 }
	}

	return ObinFalse;
}

/*
 * Stolen from Python
 * The addend 82520, was selected from the range(0, 1000000) for
   generating the greatest number of prime multipliers for tuples
   upto length eight:

     1082527, 1165049, 1082531, 1165057, 1247581, 1330103, 1082533,
     1330111, 1412633, 1165069, 1247599, 1495177, 1577699
*/
static oint
__makehash__(OState* S, OAny self){
	oint mult = 1000003L, x = 0x345678L, y;
	omem_t length = _size(self);
	OAny * items = _data(self);

	while (length > 0) {
		y = OAny_intVal(ohash(S, *items));
		items++;

		x = (x ^ y) * mult;
		/* the cast might truncate len; that doesn't change hash stability */
		mult += (oint)(82520L + length + length);

		length--;
	}

	x += 97531L;
	return x;
}

static OAny
__hash__(OState* S, OAny self){
	if(!_hash(self)) {
		_hash(self) = __makehash__(S, self);
	}

    return OInteger(_hash(self));
}

static OAny
__setitem__(OState* S, OAny self, OAny pos, OAny value){
	oint index;

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__setitem__   invalid index", pos);
	}


	_setitem(self, index, value);

	return OInteger(index);
}

OAny OArray_set(OState* S, OAny self, oindex_t index, OAny value) {
	return __setitem__(S, self, OInteger(index), value);
}

obool oarray_init(OState* S) {
	__BEHAVIOR__.__name__ = __TypeName__;

	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = OCollection_compare;
	__BEHAVIOR__.__equal__ = OCollection_equal;
	__BEHAVIOR__.__hash__ = __hash__;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;

	return OTRUE;

}

/*AUTOGEN CODE FOR PACK METHODS */

OAny OArray_pack(OState* S, omem_t size, ...){
    ObinArray * self;
    omem_t i;
    OAny item;
    va_list vargs;

    if(size == 0) {
        return _obin_array_empty(S);
    }

    if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
        return oraise(S, oerrors(S)->TypeError,
                "Array invalid size", OInteger(size));
    }

    self = _obin_array_new(S , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
        item = va_arg(vargs, OAny);
        self->data[i] = item;
    }
    va_end(vargs);

    return OArray_make(self);
}

OAny OArray_ofCStrings(OState* S, omem_t size, ...){
    ObinArray * self;
    omem_t i;
    ostring item;
    va_list vargs;

    if(size == 0) {
        return _obin_array_empty(S);
    }

    if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
        return oraise(S, oerrors(S)->TypeError,
                "Array invalid size", OInteger(size));
    }

    self = _obin_array_new(S , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
        item = va_arg(vargs, ostring);
        self->data[i] = OString(S, item);
    }
    va_end(vargs);

    return OArray_make(self);
}

OAny OArray_ofInts(OState* S, omem_t size, ...){
    ObinArray * self;
    omem_t i;
    oint item;
    va_list vargs;

    if(size == 0) {
        return _obin_array_empty(S);
    }

    if(!OBIN_IS_FIT_TO_MEMSIZE(size)) {
        return oraise(S, oerrors(S)->TypeError,
                "Array invalid size", OInteger(size));
    }

    self = _obin_array_new(S , size);

    va_start(vargs, size);
    for (i = 0; i < size; i++) {
        item = va_arg(vargs, oint);
        self->data[i] = OInteger(item);
    }
    va_end(vargs);

    return OArray_make(self);
}
