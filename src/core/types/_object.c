#include <obin.h>

typedef struct {
	OBIN_CELL_HEADER;
	/*array of traits */
	ObinAny traits;
	ObinAny scope;
} ObinObject;


#define _object(any) ((ObinObject*) (any.data.cell))
#define _traits(any) ((_object(any))->traits)
#define _scope(any) ((_object(any))->scope)

static ObinAny __tostring__(ObinState* state, ObinAny self) {
	ObinObject* cell;

	cell = _object(self);

	return obin_string_pack(state, 2,
				OSTR(state, "<Cell"),
				obin_integer_to_hex_string(state, OINT((int)cell)),
				OSTR(state,">")
	);
}

