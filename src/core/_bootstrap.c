#include <obin.h>

static ObinInternals __INTERNALS__;

ObinState* obin_init() {
	ObinState* state = obin_state_new(OBIN_DEFAULT_HEAP_SIZE);

	if(!obin_module_error_init(state, &__INTERNALS__)) {
		obin_panic("Can't init error module");
		return NULL;
	}
	if(!obin_module_string_init(state, &__INTERNALS__)) {
		obin_panic("Can't init string module");
		return NULL;
	}
	if(!obin_module_integer_init(state, &__INTERNALS__)) {
		obin_panic("Can't init integer module");
		return NULL;
	}
	if(!obin_module_random_init()) {
		obin_panic("Can't init random module");
		return NULL;
	}

	state->internals = &__INTERNALS__;
	return state;
}
