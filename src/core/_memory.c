#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <omemory.h>

#define ObinMem_MALLOC(n) ((obin_mem_t)(n) > OBIN_MEM_MAX? NULL \
				: malloc((n) ? (n) : 1))

#define ObinMem_REALLOC(p, n)	((obin_mem_t)(n) > (obin_mem_t)OBIN_MEM_MAX  ? NULL \
				: realloc((p), (n) ? (n) : 1))

#define ObinMem_FREE free

obin_pointer obin_malloc(ObinState * state, obin_mem_t size) {
	obin_pointer new_pointer;

	if (!size) {
		/*TODO MAYBE SIGNAL HERE */
		return NULL;
	}

	new_pointer = ObinMem_MALLOC(size);
/*	run gc here*/
	assert(new_pointer != 0);

	memset(new_pointer, 0, size);
	return new_pointer;
}

obin_pointer obin_malloc_and_fill(ObinState * state, obin_mem_t size) {
	obin_pointer new_pointer;

	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_MALLOC(size);
	assert(new_pointer != 0);
	memset(new_pointer, '\0', size);
	return new_pointer;
}

obin_pointer obin_realloc(ObinState * state, obin_pointer ptr, obin_mem_t size) {
	obin_pointer new_pointer;
	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_REALLOC(ptr, size);
	assert(new_pointer != 0);
	return new_pointer;
}

obin_pointer obin_memory_duplicate(ObinState * state, obin_pointer ptr,
		obin_mem_t elements, obin_mem_t element_size) {
	obin_pointer new_pointer;
	obin_mem_t size;

	size = element_size * elements;

	new_pointer = obin_malloc(state, size);
	memcpy(new_pointer, ptr, size);

	return new_pointer;
}

obin_pointer obin_gc_register(ObinState* state, ObinCell* cell){
	cell->gc_info.deads = 0;
	cell->gc_info.lives = 0;
	cell->gc_info.rc = 0;
	return cell;
}

ObinAny obin_incref(ObinState* state, ObinAny any) {
	any.data.cell->gc_info.lives++;
	any.data.cell->gc_info.rc++;
	return any;
}

ObinAny obin_decref(ObinState* state, ObinAny any) {
	any.data.cell->gc_info.deads++;
	any.data.cell->gc_info.rc--;

	return any;
}
