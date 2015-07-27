#include <obin.h>

static OInternals __INTERNALS__;

typedef obool (*obin_bootstrap_initialiser)(OState* state);
typedef void (*obin_bootstrap_finaliser)(OState* state);

typedef struct {
	const char* name;
	obin_bootstrap_initialiser initialise;
	obin_bootstrap_finaliser finalise;
} ObinModule;

static ObinModule __MODULES__[] = {
		{"Integer", &OInteger_init, 0},
		{"String", &ostring_init, 0},
		{"Error", &OError_init, 0},
		{"Array", &OArray_init, 0},
		{"Tuple", &OTuple_init, 0},
		{"Table", &OTable_init, 0},
		{"Random", &ORandom_init, 0},
};


static obool
_init_internals(OState* state) {
	ObinModule* module = __MODULES__;
	oindex_t count_modules = sizeof(__MODULES__) / sizeof(ObinModule);
	oindex_t i;

	state->internals = &__INTERNALS__;
	state->internals->cells.__Cell__ = OCell_new(EOBIN_TYPE_CELL, obin_new(state, OCell), 0, ObinNil);

	for(i=0; i < count_modules; i++) {
		module = __MODULES__ + i;
		if(!module->initialise(state)) {
			olog(state, "Can't init module %s", module->name);
			opanic("Can't bootstrap obin");
			return OFALSE;
		}
	}

	return OTRUE;
}

OState* obin_init(omem_t heap_size) {
	static int is_initialised = 0;

	if(heap_size == 0) {
		heap_size = OBIN_DEFAULT_HEAP_SIZE;
	}

	OState* state = OState_new(heap_size);

	if(!is_initialised
		&& !_init_internals(state)) {
		return NULL;
	} else {
		state->internals = &__INTERNALS__;
	}


	is_initialised = 1;
	return state;
}
