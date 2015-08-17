#include <obin.h>

static OInternals __INTERNALS__;

typedef obool (*obin_bootstrap_initialiser)(OState* S);
typedef void (*obin_bootstrap_finaliser)(OState* S);

typedef struct {
	const char* name;
	obin_bootstrap_initialiser initialise;
	obin_bootstrap_finaliser finalise;
} ObinModule;

static ObinModule __MODULES__[] = {
		{"Character", &ocharacter_init, 0},
		{"Integer", &ointeger_init, 0},
		{"Float", &ofloat_init, 0},
		{"Number", &onumber_init, 0},
		{"String", &ostring_init, 0},
		{"Error", &oerror_init, 0},
		{"Array", &ovector_init, 0},
		{"Tuple", &otuple_init, 0},
		{"Table", &otable_init, 0},
		{"Random", &orandom_init, 0},
		{"Bool", &obool_init, 0}
};


static obool
_init_internals(OState* S) {
	ObinModule* module = __MODULES__;
	oindex_t count_modules = sizeof(__MODULES__) / sizeof(ObinModule);
	oindex_t i;

	S->internals = &__INTERNALS__;

	for(i=0; i < count_modules; i++) {
		module = __MODULES__ + i;
		if(!module->initialise(S)) {
			olog(S, "Can't init module %s", module->name);
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

	OState* S = OState_create(heap_size);

	if(!is_initialised
		&& !_init_internals(S)) {
		return NULL;
	} else {
		S->internals = &__INTERNALS__;
	}


	is_initialised = 1;
	return S;
}
