#include <obin.h>
#define __TypeName__ "__Vector__"

OBIN_MODULE_LOG(VECTOR);

OCELL_DECLARE(Vector,
	omem_t size;
	omem_t capacity;
	OAny* data;
);

static OBehavior __BEHAVIOR__ = {0};

#ifdef ODEBUG
#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isVector(self))\
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \

#else
#define _CHECK_SELF_TYPE(S, self, method)
#endif

#define _CHECK_ARG_TYPE(S, arg, method) \
		if(!OAny_isVector(arg))\
			return oraise(S, oerrors(S)->TypeError, \
					__TypeName__"."#method "argument must be" __TypeName__, self);

#define _vector(any) ((Vector*) OAny_cellVal(any))
#define _size(any) ((_vector(any))->size)
#define _capacity(any) ((_vector(any))->capacity)
#define _data(any) ((_vector(any))->data)
#define _item(any, index) ((_data(any))[index])
#define _setitem(any, index, item) ((_data(any))[index] = item)

#define _vector_last_index(any) (_size(any) - 1)
static obool
_vector_grow(OState* S, OAny self, oindex_t count_elements) {
	/*TODO IT IS DANGEROUS OPERATION NEED SAFE CHECKS*/
	omem_t new_capacity;

    if (_capacity(self) > OBIN_MAX_CAPACITY - (OBIN_DEFAULT_ARRAY_SIZE + count_elements)) {
    	new_capacity = OBIN_MAX_CAPACITY;
    } else {
    	new_capacity = _capacity(self) + OBIN_DEFAULT_ARRAY_SIZE + count_elements;
    }

	if (new_capacity <= _capacity(self)) {
		return OFALSE;
	}

	_data(self) = omemory_realloc(S, _data(self), new_capacity * sizeof(OAny));

	_capacity(self) = new_capacity;

	return OTRUE;
}

OAny
OVector(OState* S, OAny size) {
	Vector * self; omem_t capacity;
	OAny s;
	if(OAny_isNil(size)){
		size = OInteger(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!OInt_isFitToMemsize(size)) {
			oraise(S, oerrors(S)->MemoryError,
				"obin_vector_new " __TypeName__ "size not fit to memory", size);
	}

	self = obin_new(S, Vector);

	capacity = (omem_t) OAny_intVal(size);
	self->data = omemory_malloc_array(S, OAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	s =  OCell_new(__OVectorTypeId__, (OCell*)self, &__BEHAVIOR__);
	return s;
}

OAny OVector_pack(OState* S, oint count, ...) {
	OAny self;
	oindex_t i;
    va_list vargs;

	if(!count) {
		return OVector(S, ObinNil);
	}

	self = OVector(S, OInteger(count));

	va_start(vargs, count);
	for (i = 0; i < count; i++) {
		_item(self, i) = va_arg(vargs, OAny);
	}
	va_end(vargs);

	_size(self) = count;

	return self;
}

static omem_t _vector_inflate(OState* S, OAny self, oindex_t start, oindex_t end) {
	omem_t new_size, old_size;
	omem_t length;

	length = end - start;
	old_size = _size(self);
	new_size = old_size + length;

	if (new_size > _capacity(self)) {
		if ( !_vector_grow(S, self, length) ){
			oraise(S, oerrors(S)->MemoryError,
				"__vector_inflate " __TypeName__ "can't grow", OInteger(length));
			return 0;
		}
	}

	omemmove(_data(self) + length, _data(self), old_size * sizeof(OAny));
	return new_size;
}

OAny OVector_insertCollection(OState* S, OAny self, OAny collection, OAny position) {
	oindex_t start, end, new_size, collection_size, i, j;

	_CHECK_SELF_TYPE(S, self, OVector_insertCollection);
	_CHECK_ARG_TYPE(S, collection, OVector_concat);

	start = OAny_intVal(position);
	collection_size = OAny_intVal(olength(S, collection));
	end = start + collection_size;

	if(start > _size(self)) {
		return oraise(S, oerrors(S)->KeyError, "obin_vector_insert_collection invalid index", position);
	}

	new_size = _vector_inflate(S, self, start, end);
	if(!new_size) {
		return oraise(S, oerrors(S)->KeyError,
				"obin_vector_insert inflate error", position);
	}

	i=start;j=0;
	while(i<end && j<collection_size) {
		_setitem(self, i, ogetitem(S, collection, OInteger(j)));
		++i; ++j;
	}

	_size(self) = new_size;

	return OInteger(new_size);
}

OAny OVector_concat(OState* S, OAny self, OAny collection) {
	OAny result;
	_CHECK_SELF_TYPE(S, self, OVector_concat);
	_CHECK_ARG_TYPE(S, collection, OVector_concat);

	result = oclone(S, self);
	OVector_insertCollection(S, result, collection, OInteger(_size(result)));
	return result;
}

OAny OVector_insert(OState* S, OAny self, OAny item, OAny position) {
	omem_t new_size;
	omem_t insert_index;

	_CHECK_SELF_TYPE(S, self, OVector_insert);

	insert_index = OAny_intVal(position);
	if(insert_index > _size(self)) {
		return oraise(S, oerrors(S)->KeyError, "obin_vector_insert invalid index", position);
	} else if(insert_index == _size(self)) {
		return OVector_push(S, self, item);
	}

	new_size = _vector_inflate(S, self, insert_index, insert_index + 1);
	if(!new_size) {
		return oraise(S, oerrors(S)->KeyError,
				"obin_vector_insert inflate error", position);
	}

	_setitem(self, insert_index, item);

	_size(self) = new_size;
	return OInteger(new_size);
}

/*
MAYBE IMPLEMENT IT IN SOURCE
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/
OAny
OVector_push(OState* S, OAny self, OAny value) {
	omem_t new_size;
	_CHECK_SELF_TYPE(S, self, OVector_push);

	new_size = _size(self) + 1;

	if (new_size > _capacity(self)){
		if (!_vector_grow(S, self, 1) ){
			oraise(S, oerrors(S)->MemoryError,
				"obin_vector_push " __TypeName__ "can't grow", OInteger(new_size));
		}
	}

	_setitem(self, _size(self), value);

	_size(self) = new_size;

	return OInteger(new_size);
}

OAny obin_vector_lastindexof(OState* S, OAny self, OAny item){
	omem_t i;

	_CHECK_SELF_TYPE(S, self, lastindexof);

	for(i=_vector_last_index(self); i>=0; --i) {
		if (OAny_isTrue(oequal(S, _item(self, i), item))) {
			return OInteger(i);
		}
	}

	return ointegers(S)->NotFound;
}

OAny OVector_indexOf(OState* S, OAny self, OAny item) {
	omem_t i;
	_CHECK_SELF_TYPE(S, self, OVector_indexOf);

	for(i=0; i<_size(self); ++i) {
		if (OAny_isTrue(oequal(S, _item(self, i), item))) {
			return OInteger(i);
		}
	}

	return ointegers(S)->NotFound;
}

OAny OVector_lastIndexOf(OState* S, OAny self, OAny item) {
	omem_t i;
	_CHECK_SELF_TYPE(S, self, OVector_indexOf);

	for(i=_size(self); i>=0; --i) {
		if (OAny_isTrue(oequal(S, _item(self, i), item))) {
			return OInteger(i);
		}
	}

	return ointegers(S)->NotFound;
}

OAny OVector_pop(OState* S, OAny self) {
    OAny item;

	_CHECK_SELF_TYPE(S, self, OVector_pop);

	if(_size(self) == 0) {
			oraise(S, oerrors(S)->IndexError,
				"obin_vector_pop " __TypeName__ " empty vector", ObinNil);
	}

	item = ogetitem(S, self, OInteger(_vector_last_index(self)));
	_size(self) -= 1;

	return item;
}

OAny OVector_clear(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, OVector_clear);
	_size(self) = 0;
	return ObinNothing;
}

OAny OVector_remove(OState* S, OAny self, OAny item) {
	oint i;
	obool find;
	find = OFALSE;

	_CHECK_SELF_TYPE(S, self, OVector_remove);

	for (i=0; i<_size(self); i++) {
		if (OAny_isTrue(oequal(S, _item(self, i), item))) {
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

OAny OVector_join(OState* S, OAny self, OAny collection) {
	OAny iterator;
	OAny value;
	OAny result;
	oint length;
	oint result_length;
	oindex_t counter;

	_CHECK_SELF_TYPE(S, self, OVector_join);

	length = OAny_intVal(olength(S, collection));
	result_length = ((length - 1) * _size(self)) + length;
	result = OVector(S, OInteger(length));

	if(result_length<=1) {
		return oclone(S,collection);
	}

	counter = length;

	iterator = oiterator(S, collection);

	while (OTRUE) {
		/*avoid appending self at end of string*/
		if(!(--counter)){
			break;
		}

		value = onext(S, iterator);
		OVector_push(S, result, value);
		OVector_insertCollection(S, result, self, OInteger(_size(result)));
	}

	/*append last element*/
	value = onext(S, iterator);
	OVector_push(S, result, value);
	return result;
}

static ostring _cstr(OState* S, OAny self) {
	return OString_cstr(S, otostring(S, self));
}

OAny OVector_reverse(OState* S, OAny self) {
	OAny result;

	oindex_t i,j;
	oint length;

	_CHECK_SELF_TYPE(S, self, OVector_reverse);

	if(_size(self) < 2) {
		return oclone(S, self);
	}

	result = OVector(S, OInteger(_size(self)));
	length = _size(self);

	for (i = 0, j=length - 1;
			(i < length && j>=0);
			i++,j--){

		_item(result, i) = _item(self, j);
	}
	_size(result) = _size(self);
	_log(S, _INFO, "OVector_reverse2 %s", _cstr(S, result));

	return result;
}

OAny OVector_fill(OState* S, OAny self, OAny item, OAny startPos, OAny endPos) {
	oint start, end;
	oindex_t i;

	_CHECK_SELF_TYPE(S, self, OVector_reverse);
	start = OAny_intVal(startPos);
	end = OAny_intVal(endPos);
	if(end <= start
		|| start < 0 || end >_size(self)) {
		return oraise(S, oerrors(S)->IndexError,
				"OArray_fill invalid positions", OTuple(S, 2, startPos, endPos));
	}


	for (i = start; i < end; i++){
		_item(self, i) = item;
	}

	return self;
}
/* PRIVATE */

static OAny __tobool__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __tobool__);
	return OBool(_size(self)>0);
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
	Vector* vector = (Vector*) self;

	omemory_free(S, vector->data);
}

static void __mark__(OState* S, OAny self, ofunc_1 mark) {
	/*TODO each here*/
	oindex_t i;

	for(i=0; i<_size(self); ++i) {
		mark(S, _item(self, i));
	}
}

static OAny __clone__(OState* S, OAny self) {
	OAny result;

	_CHECK_SELF_TYPE(S, self, __clone__);

	result = OVector(S, OInteger(_capacity(self)));
	omemcpy(_data(result), _data(self), _capacity(self) * sizeof(OAny));
	_size(result) = _size(self);
	return result;
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

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__getitem__ invalid index", pos);
	}

	return _item(self, index);
}

static OAny
__setitem__(OState* S, OAny self, OAny pos, OAny value){
	oint index;

	index = _get_index(S, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__setitem__   invalid index", pos);
	}

	if (_size(self) == 0 && index == 0) {
		return OVector_push(S, self, value);
	}

	_setitem(self, index, value);

	return OInteger(index);
}

static OAny
__hasitem__(OState* S, OAny self, OAny item){
	oint index = OAny_intVal(OVector_indexOf(S, self, item));
	return OBool( index != OBIN_INVALID_INDEX);
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

	new_size = _size(self) - 1;
	for (i = index; i < new_size; i++){
		_item(self, i) = _item(self, i + 1);
	}
	_size(self) = new_size;

	return ObinNothing;
}

obool ovector_init(OState* S) {
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
	__BEHAVIOR__.__add__ = OVector_concat;

	return OTRUE;
}
