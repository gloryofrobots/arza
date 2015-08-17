#include <obin.h>
#define __TypeName__ "__Bytecode__"
static int DEFAULT_SIZE = 50;

OBIN_MODULE_LOG(BYTECODE);

static obytecode BYTECODE_BIT_COUNT = 32;
static obytecode COMMAND_BIT_COUNT = 6;
static obytecode ARGUMENT_BIT_COUNT = BYTECODE_BIT_COUNT - COMMAND_BIT_COUNT;
static obytecode BYTECODE_MAX_VALUE = (1 << BYTECODE_BIT_COUNT) - 1;
static obytecode COMMAND_MAX_VALUE = (1 << COMMAND_BIT_COUNT) - 1;
static obytecode ARGUMENT_MAX_VALUE = (1 << ARGUMENT_BIT_COUNT) - 1;
static obytecode COMMAND_MASK = COMMAND_MAX_VALUE << ARGUMENT_BIT_COUNT;
static obytecode ARGUMENT_MASK = ARGUMENT_MAX_VALUE;

#define _obytecode_pack(command, argument) (command << ARGUMENT_BIT_COUNT) + argument

static obytecode obytecode_pack(OState* S, EOBYTECODE command, obytecode argument) {
	if (argument > ARGUMENT_MAX_VALUE) {
		opanic("obytecode_pack argument value too large");
	}
	if (command > COMMAND_MAX_VALUE) {
		opanic("obytecode_pack command value too large");
	}

    return _obytecode_pack(command, argument);
}

#define obytecode_unpack_command(code) (EOBYTECODE) ((code & COMMAND_MASK) >> ARGUMENT_BIT_COUNT)
#define obytecode_unpack_argument(code) (obytecode) (code & ARGUMENT_MASK)

OCELL_DECLARE(Bytecode,
	omem_t size;
	omem_t capacity;
	obytecode* data;
);

static OBehavior __BEHAVIOR__ = {0};

#ifdef ODEBUG
#define _CHECK_SELF_TYPE(S, self, method) \
	if(!OAny_isBytecode(self))\
		return oraise(S, oerrors(S)->TypeError, \
				__TypeName__"."#method "call from other type", self); \

#else
#define _CHECK_SELF_TYPE(S, self, method)
#endif

#define _bytecode(any) ((Bytecode*) OAny_cellVal(any))
#define _size(any) ((_bytecode(any))->size)
#define _capacity(any) ((_bytecode(any))->capacity)
#define _data(any) ((_bytecode(any))->data)
#define _item(any, index) ((_data(any))[index])
#define _setitem(any, index, item) ((_data(any))[index] = item)

#define _last_index(any) (_size(any) - 1)
static obool
_bytecode_grow(OState* S, OAny self, oindex_t count_elements) {
	omem_t new_capacity;

    if (_capacity(self) > OBIN_MAX_CAPACITY - (DEFAULT_SIZE + count_elements)) {
    	new_capacity = OBIN_MAX_CAPACITY;
    } else {
    	new_capacity = _capacity(self) + DEFAULT_SIZE + count_elements;
    }

	if (new_capacity <= _capacity(self)) {
		return OFALSE;
	}

	_data(self) = omemory_realloc(S, _data(self), new_capacity * sizeof(obytecode));

	_capacity(self) = new_capacity;

	return OTRUE;
}

OAny OBytecode(OState* S, omem_t capacity) {
	Bytecode * self;
	OAny s;
	if(capacity == 0) {
		capacity = DEFAULT_SIZE;
	}

	if (!OBIN_IS_FIT_TO_MEMSIZE(capacity)) {
			oraise(S, oerrors(S)->MemoryError,
				"OBytecode size not fit to memory", OInteger(capacity));
	}

	self = obin_new(S, Bytecode);
	self->data = omemory_malloc_array(S, OAny, capacity);
	self->capacity = capacity;
	self->size = 0;
	s =  OCell_new(__OBytecodeTypeId__, (OCell*)self, &__BEHAVIOR__);
	return s;
}

OAny OBytecode_pack(OState* S, oint count, ...) {
	OAny self;
	oindex_t i;
    va_list vargs;

	if(!count) {
		return OBytecode(S, ObinNil);
	}

	self = OBytecode(S, count);

	va_start(vargs, count);
	for (i = 0; i < count; i++) {
		_item(self, i) = va_arg(vargs, obytecode);
	}
	va_end(vargs);

	_size(self) = count;

	return self;
}

OAny
OBytecode_append(OState* S, OAny self, EOBYTECODE low, obytecode high) {
	omem_t new_size;
	obytecode code = obytecode_pack(S, low, high);

	_CHECK_SELF_TYPE(S, self, OBytecode_push);

	new_size = _size(self) + 1;

	if (new_size > _capacity(self)){
		if (!_bytecode_grow(S, self, 1) ){
			oraise(S, oerrors(S)->MemoryError,
				"obin_bytecode_push " __TypeName__ "can't grow", OInteger(new_size));
		}
	}

	_setitem(self, _size(self), code);

	_size(self) = new_size;

	return OInteger(new_size);
}
/*CREATE SPEED VERSION FOR DEBUG*/

EOBYTECODE OBytecode_getCommand(OState* S, OAny self, oint index) {
	index = _get_index(S, self, index);
	if (index == OBIN_INVALID_INDEX) {
			return oraise(S, oerrors(S)->IndexError,
					__TypeName__ "__getitem__ invalid index", OInteger(index));
	}
	return obytecode_unpack_command(_item(self,index));
}

obytecode OBytecode_getArgument(OState* S, OAny self, oint index) {
	index = _get_index(S, self, index);
	if (index == OBIN_INVALID_INDEX) {
			return oraise(S, oerrors(S)->IndexError,
					__TypeName__ "__getitem__ invalid index", OInteger(index));
	}

	return obytecode_unpack_command(_item(self,index));
}

OAny OBytecode_set(OState* S, OAny self, oindex_t index, EOBYTECODE high, obytecode low) {
	obytecode code = obytecode_pack(S, high, low);
	if(index >= _size(self)) {
		return oraise(S, oerrors(S)->IndexError,
							"OBytecode_set invalid index", OInteger(index));
	}

	_setitem(self, index, code);

	return ObinNil;
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
	Bytecode* bytecode = (Bytecode*) self;

	omemory_free(S, bytecode->data);
}


static OAny __clone__(OState* S, OAny self) {
	OAny result;

	_CHECK_SELF_TYPE(S, self, __clone__);

	result = OBytecode(S, OInteger(_capacity(self)));
	omemcpy(_data(result), _data(self), _capacity(self) * sizeof(OAny));
	_size(result) = _size(self);
	return result;
}

static OAny __length__(OState* S, OAny self) {
	_CHECK_SELF_TYPE(S, self, __length__);

	return OInteger(_size(self));
}

static oint
_get_index(OState* S, OAny self, oint index){
	if( index < 0){
		index = _size(self) - index;
	}
	if (index > _size(self) || index < 0) {
		index = OBIN_INVALID_INDEX;
	}

	return index;
}

static OAny
__getitem__(OState* S, OAny self, OAny pos){
	oint index;

	if(!OAny_isInt(pos)){
		return oraise(S, oerrors(S)->IndexError,
						__TypeName__ "__getitem__ invalid index", pos);
	}

	index = _get_index(S, self, OAny_intVal(pos));

	if (index == OBIN_INVALID_INDEX) {
		return oraise(S, oerrors(S)->IndexError,
				__TypeName__ "__getitem__ invalid index", pos);
	}

	return OInteger(_item(self, index));
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
		return OBytecode_push(S, self, value);
	}

	_setitem(self, index, OAny_intVal(value));

	return OInteger(index);
}

static OAny
__hasitem__(OState* S, OAny self, OAny item){
	oindex_t i;

	for(i=0; i<_size(self); ++i) {
		if (_item(self, i) == OAny_intVal(item)) {
			return ObinTrue;
		}
	}

	return ObinFalse;
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

obool obytecode_init(OState* S) {
	__BEHAVIOR__.__name__ = __TypeName__;
	__BEHAVIOR__.__tostring__ = __tostring__;
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

	return OTRUE;
}
