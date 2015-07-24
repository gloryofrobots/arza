#include <obin.h>
OBIN_BEHAVIOR_DECLARE(__BEHAVIOR__);

typedef struct {
	OBIN_CELL_HEADER;
	OAny path;
	obin_file file;
	obin_bool is_disposable;
} ObinFStream;

#define _fstream(any) ((ObinFStream*) OAny_toCell(any))
#define _fstream_file(any) (_fstream(any)->file)
#define _fstream_path(any) (_fstream(any)->path)
#define _fstream_is_disposable(any) (_fstream(any)->is_disposable)

OAny obin_fstream_from_file(ObinState* state, obin_file file, obin_bool is_disposable){

	ObinFStream* self;

	self = obin_new(state, ObinFStream);

	self->path = obin_strings(state)->Empty;

	self->file = file;
	self->is_disposable = is_disposable;
	return obin_cell_new(EOBIN_TYPE_CELL, (OCell*)self, &__BEHAVIOR__, obin_cells(state)->__Cell__);
}

OAny obin_fstream_from_path(ObinState* state, OAny path, obin_string mode){
	OAny result;
	obin_file file = fopen(obin_string_cstr(state, path), mode);

	if(file == NULL) {
		obin_raise(state, obin_errors(state)->IOError,
				"Unable to open file", path);
	}

	result = obin_fstream_from_file(state, file, OTRUE);
	_fstream_path(result) = path;
	return ObinNil;
}

OAny obin_fstream_write_va(ObinState* state, OAny self, obin_string format, ...){
		int result;

	    va_list myargs;
	    va_start(myargs, format);
	    result = obin_vfprintf(_fstream_file(self), format, myargs);
	    va_end(myargs);

	    return obin_integer_new(result);
}

OAny obin_fstream_write(ObinState* state, OAny self, OAny any){
	return ObinNil;
}

OAny obin_fstream_close(ObinState* state, OAny self){
	if(!_fstream_is_disposable(self)) {
		obin_raise(state, obin_errors(state)->IOError,
				"Resource is not disposable", ObinNil);
	}

	fclose(_fstream_file(self));
	_fstream_file(self) = NULL;

	return ObinNothing;
}

OAny obin_fstream_is_open(ObinState* state, OAny self) {
	if(_fstream_file(self) == NULL) {
		return ObinFalse;
	}

	return ObinTrue;
}

static OAny __tostring__(ObinState* state, OAny self) {
	return obin_string_new(state, "<File: "OBIN_POINTER_FORMATTER" >");
}

static void __destroy__(ObinState* state, OCell* cell) {
	ObinFStream* self = (ObinFStream*) cell;

	if(self->file && self->is_disposable) {
		obin_fstream_close(state,
				obin_cell_to_any(EOBIN_TYPE_CELL, (OCell*)self));
	}
}

OBIN_BEHAVIOR_DEFINE(__BEHAVIOR__,
		"__FStream__",
		OBIN_BEHAVIOR_MEMORY(__destroy__, 0),
		OBIN_BEHAVIOR_BASE(__tostring__, 0, 0, 0, 0),
		OBIN_BEHAVIOR_COLLECTION_NULL,
		OBIN_BEHAVIOR_GENERATOR_NULL,
		OBIN_BEHAVIOR_NUMBER_CAST_NULL,
		OBIN_BEHAVIOR_NUMBER_OPERATIONS_NULL
);

