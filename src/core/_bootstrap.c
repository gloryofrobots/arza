#include <obin.h>

OBIN_MODULE_DECLARE(BOOTSTRAP);

ObinState* obin_init() {
	ObinState* state = obin_state_new(OBIN_DEFAULT_HEAP_SIZE);
	return state;
}
