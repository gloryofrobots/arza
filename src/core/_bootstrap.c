#include <obin.h>

static ObinInternals __INTERNALS__;

static obin_bool
_init_internals(ObinState* state) {
	if(!obin_module_error_init(state, &__INTERNALS__)) {
			obin_panic("Can't init error module");
			return OFALSE;
	}
	if(!obin_module_string_init(state, &__INTERNALS__)) {
		obin_panic("Can't init string module");
		return OFALSE;
	}
	if(!obin_module_integer_init(state, &__INTERNALS__)) {
		obin_panic("Can't init integer module");
		return OFALSE;
	}
	if(!obin_module_random_init()) {
		obin_panic("Can't init random module");
		return OFALSE;
	}
	ObinCell* protocell = obin_new(state, ObinCell);
	__INTERNALS__->cells.__Cell__ = obin_cell_new(state, EOBIN_TYPE_CELL, protocell, 0, ObinNil);

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

	state->internals = &__INTERNALS__;

	is_initialised = 1;
	return state;
}
