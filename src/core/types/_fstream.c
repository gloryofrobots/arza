#include <obin.h>

static ObinNativeTraits __TRAITS__;

typedef struct {
	OBIN_CELL_HEADER;
	ObinAny path;
	obin_file file;
	obin_bool is_disposable;
} ObinFStream;

#define _fstream(any) ((ObinFStream*) obin_any_cell(any))
#define _fstream_file(any) (_fstream(any)->file)
#define _fstream_path(any) (_fstream(any)->path)
#define _fstream_is_disposable(any) (_fstream(any)->is_disposable)

ObinAny obin_fstream_from_file(ObinState* state, obin_file file, obin_bool is_disposable){

	ObinFStream* self;

	self = obin_new(state, ObinFStream);

	self->path = obin_string_empty(state);

	self->file = file;
	self->is_disposable = is_disposable;
	return obin_cell_new(EOBIN_TYPE_OBJECT, self, __TRAITS__);
}

ObinAny obin_fstream_from_path(ObinState* state, ObinAny path, obin_string mode){
	ObinAny result;
	obin_file file = fopen(obin_string_cstr(state, path), mode);

	if(file == NULL) {
		return obin_raise_io_error(state, "Unable to open file", path);
	}

	result = obin_fstream_from_file(state, file, OTRUE);
	_fstream_path(result) = path;
	return ObinNil;
}

ObinAny obin_fstream_write_va(ObinState* state, ObinAny self, obin_string format, ...){
		int result;

	    va_list myargs;
	    va_start(myargs, format);
	    result = obin_vfprintf(_fstream_file(self), format, myargs);
	    va_end(myargs);

	    return obin_integer_new(result);
}

ObinAny obin_fstream_write(ObinState* state, ObinAny self, ObinAny any){
	return ObinNil;
}

ObinAny obin_fstream_close(ObinState* state, ObinAny self){
	if(!_fstream_is_disposable(self)) {
		return obin_raise_io_error(state, "Resource is not disposable", ObinNil);
	}

	fclose(_fstream_file(self));
	_fstream_file(self) = NULL;

	return ObinNothing;
}

ObinAny obin_fstream_is_open(ObinState* state, ObinAny self) {
	if(_fstream_file(self) == NULL) {
		return ObinFalse;
	}

	return ObinTrue;
}

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	return obin_string_new(state, "<File: "OBIN_POINTER_FORMATTER" >");
}

static ObinAny __destroy__(ObinState* state, ObinAny self) {
	if(obin_any_is_true(obin_fstream_is_open(state, self))
			&& _fstream_is_disposable(self)) {

		obin_fstream_close(state, self);
	}

	return ObinNothing;
}


ObinBaseTrait __BASE__ = {
	 __tostring__,
	 0, /*__tobool__ */
	 __destroy__,
	 0, /* clone */
	 0, /*__compare__ */
	 0,/* _hash__ */
	 0, /* __mark__ */
} ;
static ObinNativeTraits __TRAITS__ = {
	 "__fstream__",
	 &__BASE__, /*base*/
	 0, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};




