#include <obin.h>
OBEHAVIOR_DECLARE(__BEHAVIOR__);

typedef struct {
	OCELL_HEADER;
	OAny path;
	ofile file;
	obool is_disposable;
} ObinFStream;

#define _fstream(any) ((ObinFStream*) OAny_cellVal(any))
#define _fstream_file(any) (_fstream(any)->file)
#define _fstream_path(any) (_fstream(any)->path)
#define _fstream_is_disposable(any) (_fstream(any)->is_disposable)

OAny OFstream_fromFile(OState* S, ofile file, obool is_disposable){

	ObinFStream* self;

	self = obin_new(S, ObinFStream);

	self->path = ostrings(S)->Empty;

	self->file = file;
	self->is_disposable = is_disposable;
	return OCell_new(EOBIN_TYPE_CELL, (OCell*)self, &__BEHAVIOR__, ocells(S)->__Cell__);
}

OAny OFstream_fromPath(OState* S, OAny path, ostring mode){
	OAny result;
	ofile file = fopen(OString_cstr(S, path), mode);

	if(file == NULL) {
		oraise(S, oerrors(S)->IOError,
				"Unable to open file", path);
	}

	result = OFstream_fromFile(S, file, OTRUE);
	_fstream_path(result) = path;
	return ObinNil;
}

OAny OFstream_writeVA(OState* S, OAny self, ostring format, ...){
		int result;

	    va_list myargs;
	    va_start(myargs, format);
	    result = ovfprintf(_fstream_file(self), format, myargs);
	    va_end(myargs);

	    return OInteger(result);
}

OAny OFstream_write(OState* S, OAny self, OAny any){
	return ObinNil;
}

OAny OFstream_close(OState* S, OAny self){
	if(!_fstream_is_disposable(self)) {
		oraise(S, oerrors(S)->IOError,
				"Resource is not disposable", ObinNil);
	}

	fclose(_fstream_file(self));
	_fstream_file(self) = NULL;

	return ObinNothing;
}

OAny OFstream_isOpen(OState* S, OAny self) {
	if(_fstream_file(self) == NULL) {
		return ObinFalse;
	}

	return ObinTrue;
}

static OAny __tostring__(OState* S, OAny self) {
	return OString(S, "<File: "OBIN_POINTER_FORMATTER" >");
}

static void __destroy__(OState* S, OCell* cell) {
	ObinFStream* self = (ObinFStream*) cell;

	if(self->file && self->is_disposable) {
		OFstream_close(S,
				OCell_toAny(EOBIN_TYPE_CELL, (OCell*)self));
	}
}

OBEHAVIOR_DEFINE(__BEHAVIOR__,
		"__FStream__",
		OBEHAVIOR_MEMORY(__destroy__, 0),
		OBEHAVIOR_BASE(__tostring__, 0, 0, 0, 0),
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR_NULL,
		OBEHAVIOR_NUMBER_NULL
);

