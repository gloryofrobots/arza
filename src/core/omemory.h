#ifndef OBIN_OMEMORY_H_
#define OBIN_OMEMORY_H_
#include "obuiltin.h"

typedef struct{
	obin_integer lives;
	obin_integer deads;
	obin_integer rc;
} ObinCellGCInfo;

/*IT EMPTY FOR NOW */
#define OBIN_CELL_HEADER \
	ObinNativeTraits* native_traits; \
	ObinCellGCInfo gc_info

struct _ObinCell {
	OBIN_CELL_HEADER;
};

#define obin_cell_set_native_traits(cell, traits) cell->native_traits = traits

ObinAny obin_incref(ObinState* state, ObinAny any);
ObinAny obin_decref(ObinState* state, ObinAny any);

#ifndef OBIN_MEMORY_DEBUG

void obin_free(obin_pointer ptr);

#define obin_sincref(state, any) \
	(obin_any_is_cell(any) ? obin_incref(any) : any)

#define obin_sdecref(state, any) \
	(obin_any_is_cell(any) ? obin_decref(any) : any)

obin_pointer obin_malloc(ObinState* state, obin_mem_t size);

obin_pointer obin_malloc_and_fill(ObinState* state, obin_mem_t size);

obin_pointer obin_realloc(ObinState* state, obin_pointer ptr, obin_mem_t size) ;

obin_pointer obin_memdup(ObinState* state, obin_pointer ptr, obin_mem_t elements, obin_mem_t element_size );

obin_pointer obin_gc_register(ObinState* state, ObinCell* cell);

#else
/* Redirect all memory operations debugging allocator. */
#endif

#define obin_new(state, type) \
		((type*) obin_gc_register(state, (ObinCell*) obin_malloc_type(state, type)))

#define obin_malloc_type(state, type) \
	 ( (type *) obin_malloc(state, sizeof(type)) )

#define obin_malloc_collection(state, type, n) \
  ( ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	( (type *) obin_malloc(state, (n) * sizeof(type)) ) )

#define obin_realloc_type(state, p, type, n) \
  ( (p) = ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	(type *) obin_realloc(state, (p), (n) * sizeof(type)) )


#endif
