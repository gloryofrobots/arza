#include <obin.h>
#define __TypeName__ "__Array__"

OCELL_DECLARE(ObinArray,
	omem_t size;
	omem_t capacity;
	OAny* data;
);

static OBehavior __BEHAVIOR__ = {0};

#ifdef ODEBUG
#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isArray(self))\
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \

#else
#define _CHECK_SELF_TYPE(S, self, method)
#endif

#define _CHECK_ARG_TYPE(S, arg, method) \
		if(!OAny_isArray(arg))\
			return oraise(S, oerrors(S)->TypeError, \
					__TypeName__"."#method "argument must be" __TypeName__, self);

#define _array(any) ((ObinArray*) OAny_cellVal(any))
#define _array_size(any) ((_array(any))->size)
#define _array_capacity(any) ((_array(any))->capacity)
#define _array_data(any) ((_array(any))->data)
#define _array_item(any, index) ((_array_data(any))[index])
#define _array_setitem(any, index, item) ((_array_data(any))[index] = item)

#define _array_last_index(any) (_array_size(any) - 1)
static obool
_array_grow(OState* S, OAny self, oindex_t count_elements) {
	/*TODO IT IS DANGEROUS OPERATION NEED SAFE CHECKS*/
	omem_t new_capacity;
    if (_array_capacity(self) > OBIN_MAX_CAPACITY - (OBIN_DEFAULT_ARRAY_SIZE + count_elements)) {
    	new_capacity = OBIN_MAX_CAPACITY;
    } else {
    	new_capacity = _array_capacity(self) + OBIN_DEFAULT_ARRAY_SIZE + count_elements;
    }

	if (new_capacity <= _array_capacity(self)) {
		return OFALSE;
	}

	_array_data(self) = omemory_realloc(S, _array_data(self), new_capacity);
	_array_capacity(self) = new_capacity;

	return OTRUE;
}

OAny
OArray(OState* S, OAny size) {
	ObinArray * self; omem_t capacity;
	if(OAny_isNil(size)){
		size = OInteger(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!OInt_isFitToMemsize(size)) {
			oraise(S, oerrors(S)->MemoryError,
				"obin_array_new " __TypeName__ "size not fit to memory", size);
	}

	self = obin_new(S, ObinArray);

	capacity = (omem_t) OAny_intVal(size);
	self->data = omemory_malloc_array(S, OAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	return OCell_new(EOBIN_TYPE_ARRAY, (OCell*)self, &__BEHAVIOR__, ocells(S)->__Array__);
}

OAny OArray_pack(OState* S, oint count, ...) {
	OAny self;
	oindex_t i;
    va_list vargs;

	if(!count) {
		return OArray(S, ObinNil);
	}

	self = OArray(S, OInteger(count));

	va_start(vargs, count);
	for (i = 0; i < count; i++) {
		_array_item(self, i) = va_arg(vargs, OAny);
	}
	va_end(vargs);

	return self;
}

static omem_t _array_inflate(OState* S, OAny self, oindex_t start, oindex_t end) {
	omem_t new_size, old_size;
	omem_t length;

	length = end - start;
	old_size = _array_size(self);
	new_size = old_size + length;

	if (new_size > _array_capacity(self)) {
		if ( !_array_grow(S, self, length) ){
			oraise(S, oerrors(S)->MemoryError,
				"__array_inflate " __TypeName__ "can't grow", OInteger(length));
			return 0;
		}
	}

	omemmove(_array_data(self) + length, _array_data(self), old_size * sizeof(OAny));
	return new_size;
}

OAny OArray_insertCollection(OState* S, OAny self, OAny collection, OAny position) {
	oindex_t start, end, new_size, collection_size, i, j;

	_CHECK_SELF_TYPE(S, self, OArray_insertCollection);
	_CHECK_ARG_TYPE(S, collection, OArray_concat);

	start = OAny_intVal(position);
	collection_size = OAny_intVal(olength(S, collection));
	end = start + collection_size;

	if(start > _array_size(self)) {
		return oraise(S, oerrors(S)->KeyError, "obin_array_insert_collection invalid index", position);
	}

	new_size = _array_inflate(S, self, start, end);
	if(!new_size) {
		return oraise(S, oerrors(S)->KeyError,
				"obin_array_insert inflate error", position);
	}

	i=start;j=0;
	while(i<end && j<collection_size) {
		_array_setitem(self, i, ogetitem(S, collection, OInteger(j)));
		++i; ++j;
	}

	_array_size(self) = new_size;

	return OInteger(new_size);
}

OAny OArray_concat(OState* S, OAny self, OAny collection) {
	OAny result;
	_CHECK_SELF_TYPE(S, self, OArray_concat);
	_CHECK_ARG_TYPE(S, collection, OArray_concat);

	result = oclone(S, self);
	OArray_insertCollection(S, result, collection, OInteger(_array_size(result)));
	return result;
}

OAny OArray_insert(OState* S, OAny self, OAny item, OAny position) {
	omem_t new_size;
	omem_t insert_index;

	_CHECK_SELF_TYPE(S, self, OArray_insert);

	insert_index = OAny_intVal(position);
	if(insert_index > _array_size(self)) {
		return oraise(S, oerrors(S)->KeyError, "obin_array_insert invalid index", position);
	} else if(insert_index == _array_size(self)) {
		return OArray_push(S, self, item);
	}

	new_size = _array_inflate(S, self, insert_index, insert_index + 1);
	if(!new_size) {
		return oraise(S, oerrors(S)->KeyError,
				"obin_array_insert inflate error", position);
	}

	_array_setitem(self, insert_index, item);

	_array_size(self) = new_size;
	return OInteger(new_size);
}

/*
MAYBE IMPLEMENT IT IN SOURCE
ObinAny obin_array_merge(ObinState* S, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* S, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* S, ObinAny self);
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/
OAny
OArray_push(OState* S, OAny self, OAny value) {
	omem_t new_size;
	_CHECK_SELF_TYPE(S, self, OArray_push);

	new_size = _array_size(self) + 1;

	if (new_size > _array_capacity(self)){
		if (!_array_grow(S, self, 1) ){
			oraise(S, oerrors(S)->MemoryError,
				"obin_array_push " __TypeName__ "can't grow", OInteger(new_size));
		}
	}

	_array_setitem(self, _array_size(self), value);

	_array_size(self) = new_size;

	return OInteger(new_size);
}

OAny obin_array_lastindexof(OState* S, OAny self, OAny item){
	omem_t i;

	_CHECK_SELF_TYPE(S, self, lastindexof);

	for(i=_array_last_index(self); i>=0; --i) {
		if (OAny_isTrue(oequal(S, _array_item(self, i), item))) {
			return OInteger(i);
		}
	}

	return ointegers(S)->NotFound;
}

OAny OArray_indexOf(OState* S, OAny self, OAny item) {
	omem_t i;

	_CHECK_SELF_TYPE(S, self, OArray_indexOf);

	for(i=0; i<_array_size(self); ++i) {
		if (OAny_isTrue(oequal(S, _array_item(self, i), item))) {
			return OInteger(i);
		}
	}

	return ointegers(S)->NotFound;
}

OAny OArray_pop(OState* S, OAny self) {
    OAny item;

	_CHECK_SELF_TYPE(S, self, OArray_pop);

	if(_array_size(self) == 0) {
			oraise(S, oerrors(S)->IndexError,
				"obin_array_pop " __TypeName__ " empty array", ObinNil);
	}

	item = ogetitem(S, self, OInteger(_array_last_index(self)));
	_array_size(self) -= 1;

	return item;
}

OAny OArray_clear(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OArray_clear);
	_array_size(self) = 0;
	return ObinNothing;
}

OAny OArray_remove(OState* S, OAny self, OAny item) {
	oint i;
	obool find;
	find = OFALSE;

	_CHECK_SELF_TYPE(S, self, OArray_remove);

	for (i=0; i<_array_size(self); i++) {
		if(OAny_isTrue(oequal(S, self, item))) {
			find = OTRUE;
			break;
		}
	}

	if(!find) {
		return ObinFalse;
	}

	odelitem(S, self, OInteger(i));
	return ObinTrue;
}

OAny OArray_join(OState* S, OAny self, OAny collection) {
	OAny iterator;
	OAny value;
	OAny result;
	oint length;
	oindex_t counter;

	_CHECK_SELF_TYPE(S, self, OArray_join);

	length = OAny_intVal(olength(S, collection));
	length = (length - 1 * _array_size(self)) + length;
	result = OArray(S, OInteger(length));
	if(!length) {
		return result;
	}
	counter = length;

	iterator = oiterator(S, collection);

	while (OTRUE) {
		/*avoid appending self at end of string*/
		if(!(--counter)){
			break;
		}

		value = onext(S, iterator);
		OArray_push(S, result, value);
		OArray_insertCollection(S, result, self, OInteger(_array_size(result)));
	}

	/*append last element*/
	value = onext(S, iterator);
	OArray_push(S, result, value);
	return result;
}

OAny OArray_reverse(OState* S, OAny self) {
	OAny item;
	oindex_t i,j;
	oint length;

	_CHECK_SELF_TYPE(S, self, OArray_reverse);
	if(_array_size(self) < 2) {
		return self;
	}
	length = _array_size(self);

	for (i = 0; i < length / 2 - 1; i++){
	    j = length - i - 1;

	    item = _array_item(self, i);
	    _array_item(self, i) = _array_item(self, j);
	    _array_item(self, j) = item;
	  }

	return self;
}

OAny OArray_fill(OState* S, OAny self, OAny item, OAny startPos, OAny endPos) {
	oint start, end;
	oindex_t i;

	_CHECK_SELF_TYPE(S, self, OArray_reverse);
	start = OAny_intVal(startPos);
	end = OAny_intVal(endPos);
	if(end <= start
		|| start < 0 || end >_array_size(self)) {
		return oraise(S, oerrors(S)->IndexError,
				"OArray_fill invalid positions", OTuple(S, 2, startPos, endPos));
	}


	for (i = start; i < end; i++){
		_array_item(self, i) = item;
	}

	return self;
}
/* PRIVATE */

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);
	return OBool(_array_size(self)>0);
}

static OAny __tostring__(OState* S, OAny self) {
    OAny result;

	_CHECK_SELF_TYPE(S, self, __tostring__);
	result = OString_join(S, OString(S, ","), self);
	result = oadd(S, OString(S, "["), result);
	result = oadd(S, result, OString(S, "]"));

	return result;
}

static void __destroy__(OState* S, OCell* self) {
	ObinArray* array = (ObinArray*) self;

	omemory_free(S, array->data);
}

static void __mark__(OState* S, OAny self, ofunc_1 mark) {
	/*TODO each here*/
	oindex_t i;

	for(i=0; i<_array_size(self); ++i) {
		mark(S, _array_item(self, i));
	}
}

static OAny __clone__(OState* S, OAny self) {
	OAny result;

	_CHECK_SELF_TYPE(S, self, __clone__);

	result = OArray(S, OInteger(_array_capacity(self)));
	omemcpy(_array_data(result), _array_data(self), _array_capacity(self) * sizeof(OAny));
	_array_size(result) = _array_size(self);
	return result;
}

static OAny __length__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __length__);

	return OInteger(_array_size(self));
}

static oint
_get_index(OState* S, OAny self, OAny pos){
	oint index;

	if(!OAny_isInt(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = OAny_intVal(pos);
	if( index < 0){
		index = _array_size(self) - index;
	} else{
		index = OAny_intVal(pos);
	}

	if (index > _array_size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static OAny
__getitem__(OState* S, OAny self, OAny pos){
	oint index;

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__getitem__ invalid index", pos);
	}

	return _array_item(self, index);
}

static OAny
__setitem__(OState* S, OAny self, OAny pos, OAny value){
	oint index;

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__setitem__   invalid index", pos);
	}

	if (_array_size(self) == 0 && index == 0) {
		return OArray_push(S, self, value);
	}

	_array_setitem(self, index, value);

	return OInteger(index);
}

static OAny
__hasitem__(OState* S, OAny self, OAny item){
	return OBool(OAny_intVal(OArray_indexOf(S, self, item)) != OBIN_INVALID_INDEX);
}

static OAny
__delitem__(OState* S, OAny self, OAny pos){
	oint index, i;
	omem_t new_size;

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__delitem__ invalid index", pos);
	}

	new_size = _array_size(self) - 1;
	for (i = index; i < new_size; i++){
		_array_item(self, i) = _array_item(self, i + 1);
	}
	_array_size(self) = new_size;

	return ObinNothing;
}

obool oarray_init(OState* S) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__destroy__ = __destroy__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = OCollection_compare;
	__BEHAVIOR__.__equal__ = OCollection_equal;
	__BEHAVIOR__.__iterator__ = OSequence_iterator;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__delitem__ = __delitem__;
	__BEHAVIOR__.__mark__ = __mark__;
	__BEHAVIOR__.__add__ = OArray_concat;

	ocells(S)->__Array__ = OCell_new(EOBIN_TYPE_CELL,
			obin_new(S, OCell), &__BEHAVIOR__, ocells(S)->__Cell__);

	return OTRUE;
}
