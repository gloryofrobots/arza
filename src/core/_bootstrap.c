#include <obin.h>

static ObinInternals __INTERNALS__;

typedef obin_bool (*obin_bootstrap_initialiser)(ObinState* state);
typedef void (*obin_bootstrap_finaliser)(ObinState* state);

typedef struct {
	const char* name;
	obin_bootstrap_initialiser initialise;
	obin_bootstrap_finaliser finalise;
} ObinModule;

static ObinModule __MODULES__[] = {
		{"Integer", &obin_module_integer_init, 0},
		{"String", &obin_module_string_init, 0},
		{"Error", &obin_module_error_init, 0},
		{"Array", &obin_module_array_init, 0},
		{"Tuple", &obin_module_tuple_init, 0},
		{"Table", &obin_module_table_init, 0},
		{"Random", &obin_module_random_init, 0},
};


static obin_bool
_init_internals(ObinState* state) {
	ObinModule* module = __MODULES__;
	obin_index count_modules = sizeof(__MODULES__) / sizeof(ObinModule);
	obin_index i;

	state->internals = &__INTERNALS__;
	state->internals->cells.__Cell__ = obin_cell_new(EOBIN_TYPE_CELL, obin_new(state, ObinCell), 0, ObinNil);

	for(i=0; i < count_modules; i++) {
		module = __MODULES__ + i;
		if(!module->initialise(state)) {
			obin_log(state, "Can't init module %s", module->name);
			obin_panic("Can't bootstrap obin");
			return OFALSE;
		}
	}

	return OTRUE;
}

ObinState* obin_init(obin_mem_t heap_size) {
	static int is_initialised = 0;

	if(heap_size == 0) {
		heap_size = OBIN_DEFAULT_HEAP_SIZE;
	}

	ObinState* state = obin_state_new(heap_size);

	if(!is_initialised
		&& !_init_internals(state)) {
		return NULL;
	}


	is_initialised = 1;
	return state;
}
