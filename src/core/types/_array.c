#include <obin.h>
#define __TypeName__ "__Array__"

OCELL_DECLARE(ObinArray,
	omem_t size;
	omem_t capacity;
	OAny* data;
);

static OBehavior __BEHAVIOR__ = {0};

#define _CHECK_SELF_TYPE(state, self, method) \
	if(!OAny_isArray(self)) { \
		return oraise(state, oerrors(state)->TypeError, \
				__TypeName__ #method "call from other type", self); \
	} \

#define _array(any) ((ObinArray*) OAny_toCell(any))
#define _array_size(any) ((_array(any))->size)
#define _array_capacity(any) ((_array(any))->capacity)
#define _array_data(any) ((_array(any))->data)
#define _array_item(any, index) ((_array_data(any))[index])
#define _array_setitem(any, index, item) ((_array_data(any))[index] = item)

#define _array_last_index(any) (_array_size(any) - 1)
static obool
_array_grow(OState* state, OAny self, oindex_t count_elements) {
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

	_array_data(self) = obin_memory_realloc(state, _array_data(self), new_capacity);
	_array_capacity(self) = new_capacity;

	return OTRUE;
}

OAny
obin_array_new(OState* state, OAny size) {
	ObinArray * self; omem_t capacity;
	if(OAny_isNil(size)){
		size = obin_integer_new(OBIN_DEFAULT_ARRAY_SIZE);
	}
	if (!OInt_isFitToMemsize(size)) {
			oraise(state, oerrors(state)->MemoryError,
				"obin_array_new " __TypeName__ "size not fit to memory", size);
	}

	self = obin_new(state, ObinArray);

	capacity = (omem_t) OAny_toInt(size);
	self->data = obin_malloc_array(state, OAny, capacity);

	self->capacity = capacity;
	self->size = 0;
	return obin_cell_new(EOBIN_TYPE_ARRAY, (OCell*)self, &__BEHAVIOR__, ocells(state)->__Array__);
}

static omem_t _array_inflate(OState* state, OAny self, oindex_t start, oindex_t end) {
	omem_t new_size, old_size;
	omem_t length;

	length = end - start;
	old_size = _array_size(self);
	new_size = old_size + length;

	if (new_size > _array_capacity(self)) {
		if ( !_array_grow(state, self, length) ){
			oraise(state, oerrors(state)->MemoryError,
				"__array_inflate " __TypeName__ "can't grow", obin_integer_new(length));
			return 0;
		}
	}

	omemmove(_array_data(self) + length, _array_data(self), old_size * sizeof(OAny));
	return new_size;
}

OAny obin_array_insert_collection(OState* state, OAny self, OAny collection, OAny position) {
	OAny item;
	oindex_t start, end, new_size, collection_size, i, j;

	_CHECK_SELF_TYPE(state, self, obin_array_insert_collection);

	start = OAny_toInt(position);
	collection_size = OAny_toInt(obin_length(state, collection));
	end = start + collection_size;

	if(start > _array_size(self)) {
		return oraise(state, oerrors(state)->KeyError, "obin_array_insert_collection invalid index", position);
	} else if(start == _array_size(self)) {
		return obin_add(state, self, item);
	}

	new_size = _array_inflate(state, self, start, end);
	if(!new_size) {
		return oraise(state, oerrors(state)->KeyError,
				"obin_array_insert inflate error", position);
	}

	i=start;j=0;
	while(i<end && j<collection_size) {
		_array_setitem(self, i, obin_getitem(state, collection, obin_integer_new(j)));
		++i; ++j;
	}

	_array_size(self) = new_size;

	return obin_integer_new(new_size);
}

OAny obin_array_insert(OState* state, OAny self, OAny item, OAny position) {
	omem_t new_size;
	omem_t insert_index;

	_CHECK_SELF_TYPE(state, self, obin_array_insert);

	insert_index = OAny_toInt(position);
	if(insert_index > _array_size(self)) {
		return oraise(state, oerrors(state)->KeyError, "obin_array_insert invalid index", position);
	} else if(insert_index == _array_size(self)) {
		return obin_array_push(state, self, item);
	}

	new_size = _array_inflate(state, self, insert_index, insert_index + 1);
	if(!new_size) {
		return oraise(state, oerrors(state)->KeyError,
				"obin_array_insert inflate error", position);
	}

	_array_setitem(self, insert_index, item);

	_array_size(self) = new_size;
	return obin_integer_new(new_size);
}

/*
 * implemented __add__
 * */
/*
MAYBE IMPLEMENT IT IN SOURCE
ObinAny obin_array_merge(ObinState* state, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* state, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* state, ObinAny self);
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/
OAny
obin_array_push(OState* state, OAny self, OAny value) {
	omem_t new_size;
	_CHECK_SELF_TYPE(state, self, obin_array_push);

	new_size = _array_size(self) + 1;

	if (new_size > _array_capacity(self)){
		if (!_array_grow(state, self, 1) ){
			oraise(state, oerrors(state)->MemoryError,
				"obin_array_push " __TypeName__ "can't grow", obin_integer_new(new_size));
		}
	}

	_array_setitem(self, _array_size(self), value);

	_array_size(self) = new_size;

	return obin_integer_new(new_size);
}

OAny obin_array_lastindexof(OState* state, OAny self, OAny item){
	omem_t i;

	_CHECK_SELF_TYPE(state, self, lastindexof);

	for(i=_array_last_index(self); i>=0; --i) {
		if (OAny_isTrue(obin_equal(state, _array_item(self, i), item))) {
			return obin_integer_new(i);
		}
	}

	return ointegers(state)->NotFound;
}

OAny obin_array_indexof(OState* state, OAny self, OAny item) {
	omem_t i;

	_CHECK_SELF_TYPE(state, self, obin_array_indexof);

	for(i=0; i<_array_size(self); ++i) {
		if (OAny_isTrue(obin_equal(state, _array_item(self, i), item))) {
			return obin_integer_new(i);
		}
	}

	return ointegers(state)->NotFound;
}

OAny obin_array_pop(OState* state, OAny self) {
    OAny item;

	_CHECK_SELF_TYPE(state, self, obin_array_pop);

	if(_array_size(self) == 0) {
			oraise(state, oerrors(state)->IndexError,
				"obin_array_pop " __TypeName__ " empty array", ObinNil);
	}

	item = obin_getitem(state, self, obin_integer_new(_array_last_index(self)));
	_array_size(self) -= 1;

	return item;
}

OAny obin_array_clear(OState* state, OAny self) {
	_CHECK_SELF_TYPE(state, self, obin_array_clear);
	_array_size(self) = 0;
	return ObinNothing;
}

OAny obin_array_remove(OState* state, OAny self, OAny item) {
	oint i;
	obool find;
	find = OFALSE;

	_CHECK_SELF_TYPE(state, self, obin_array_remove);

	for (i=0; i<_array_size(self); i++) {
		if(OAny_isTrue(obin_equal(state, self, item))) {
			find = OTRUE;
			break;
		}
	}

	if(!find) {
		return ObinFalse;
	}

	obin_delitem(state, self, obin_integer_new(i));
	return ObinTrue;
}

/* PRIVATE */

static OAny __tobool__(OState* state, OAny self) {
	_CHECK_SELF_TYPE(state, self, __tobool__);
	return obin_bool_new(_array_size(self)>0);
}

static OAny __tostring__(OState* state, OAny self) {
    OAny result;

	_CHECK_SELF_TYPE(state, self, __tostring__);
	result = obin_string_join(state, obin_char_new(','), self);
	result = obin_add(state, obin_char_new('['), result);
	result = obin_add(state, result, obin_char_new(']'));

	return result;
}

static void __destroy__(OState* state, OCell* self) {
	ObinArray* array = (ObinArray*) self;

	obin_memory_free(state, array->data);
}

static void __mark__(OState* state, OAny self, ofunc_1 mark) {
	/*TODO each here*/
	oindex_t i;

	for(i=0; i<_array_size(self); ++i) {
		mark(state, _array_item(self, i));
	}
}

static OAny __clone__(OState* state, OAny self) {
	OAny result;

	_CHECK_SELF_TYPE(state, self, __clone__);

	result = obin_array_new(state, obin_integer_new(_array_capacity(self)));
	omemcpy(_array_data(result), _array_data(self), _array_capacity(self) * sizeof(OAny));
	_array_size(result) = _array_size(self);
	return result;
}

static OAny __length__(OState* state, OAny self) {
	_CHECK_SELF_TYPE(state, self, __length__);

	return obin_integer_new(_array_size(self));
}

static oint
_get_index(OState* state, OAny self, OAny pos){
	oint index;

	if(!OAny_isInt(pos)){
		return OBIN_INVALID_INDEX;
	}

	index = OAny_toInt(pos);
	if( index < 0){
		index = _array_size(self) - index;
	} else{
		index = OAny_toInt(pos);
	}

	if (index > _array_size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static OAny
__getitem__(OState* state, OAny self, OAny pos){
	oint index;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(state, oerrors(state)->IndexError,
				__TypeName__ "__getitem__ invalid index", pos);
	}

	return _array_item(self, index);
}

static OAny
__setitem__(OState* state, OAny self, OAny pos, OAny value){
	oint index;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(state, oerrors(state)->IndexError,
				__TypeName__ "__setitem__   invalid index", pos);
	}

	if (_array_size(self) == 0 && index == 0) {
		return obin_array_push(state, self, value);
	}

	_array_setitem(self, index, value);

	return obin_integer_new(index);
}

static OAny
__hasitem__(OState* state, OAny self, OAny item){
	return obin_bool_new(OAny_toInt(obin_array_indexof(state, self, item)) != OBIN_INVALID_INDEX);
}

static OAny
__delitem__(OState* state, OAny self, OAny pos){
	oint index, i;
	omem_t new_size;

	index = _get_index(state, self, pos);

	if (index == OBIN_INVALID_INDEX) {
		return oraise(state, oerrors(state)->IndexError,
				__TypeName__ "__delitem__ invalid index", pos);
	}

	new_size = _array_size(self) - 1;
	for (i = index; i < new_size; i++){
		_array_item(self, i) = _array_item(self, i + 1);
	}
	_array_size(self) = new_size;

	return ObinNothing;
}

obool obin_module_array_init(OState* state) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__destroy__ = __destroy__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = obin_collection_compare;
	__BEHAVIOR__.__iterator__ = obin_sequence_iterator_new;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__setitem__ = __setitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
	__BEHAVIOR__.__delitem__ = __delitem__;
	__BEHAVIOR__.__mark__ = __mark__;

	ocells(state)->__Array__ = obin_cell_new(EOBIN_TYPE_CELL,
			obin_new(state, OCell), &__BEHAVIOR__, ocells(state)->__Cell__);

	return OTRUE;
}
