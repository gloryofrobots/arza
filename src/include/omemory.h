#ifndef OBIN_OMEMORY_H_
#define OBIN_OMEMORY_H_
#include "obuiltin.h"

/*
 * ObinMemoryFreeNode are used to manage the space freed after the sweep phase.
 * these entries contain their own size and a reference of the entry next to them
 */
typedef struct ObinMemoryFreeNode {
	struct ObinMemoryFreeNode* next;
    size_t size;
} ObinMemoryFreeNode;

struct _ObinMemory {
	void* heap;
	obin_mem_t heap_size;
	obin_mem_t heap_capacity;
	obin_mem_t heap_gc_threshold;
	ObinMemoryFreeNode* free_node;

	obin_mem_t heap_free_size;
	/*
	 * if this counter equals 0, only then it is safe to collect the
	 * garbage. The counter is increased in cell constructors
	 */
	obin_integer transaction_count; /* the number of collections performed */

	obin_mem_t collections_count; /* the number of collections performed */
	obin_mem_t live_count;        /* number of live objects (per collection) */
	obin_mem_t live_space;        /* space consumed by live objects (per collection) */
	obin_mem_t killed_count;       /* number of freed objects (per collection) */
	obin_mem_t killed_space;       /* freed space (per collection) */
	obin_mem_t allocated_count;       /* number of allocated objects (since last collection) */
	obin_mem_t allocated_space;       /* allocated space (since last collection) */
};

#define obin_any_cell_size(any) (obin_any_cell(any)->memory.size)

typedef struct{
	obin_bool mark;
	obin_mem_t size;
} ObinCellMemoryInfo;

/*IT EMPTY FOR NOW*/
#define OBIN_CELL_HEADER \
	ObinNativeTraits* native_traits; \
	ObinCellMemoryInfo memory;

struct _ObinCell {
	OBIN_CELL_HEADER;
};

#define OBIN_DECLARE_CELL(CELLNAME, body) \
typedef struct _##CELLNAME { \
	OBIN_CELL_HEADER \
	body \
} CELLNAME;




ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell, ObinNativeTraits* traits);

/*TRAITS HERE MUST EXIST IN CELL */
ObinAny obin_cell_to_any(EOBIN_TYPE type, ObinCell* cell);

ObinState* obin_state_new(obin_mem_t heap_size);
void obin_state_destroy(ObinState* state);

void* obin_allocate_cell(ObinState* state, obin_mem_t size);
void obin_gc_collect(ObinState* state);

obin_pointer obin_malloc(ObinState* state, obin_mem_t size);

obin_pointer obin_realloc(ObinState* state, obin_pointer ptr, obin_mem_t size) ;

obin_pointer obin_memdup(ObinState* state, obin_pointer ptr, obin_mem_t elements, obin_mem_t element_size );

void obin_free(ObinState* state, obin_pointer ptr);

void obin_memory_debug_trace(ObinState* state);

/*
 * During memory transactions gc collection will not occur.
 * There are no support for rollbacks now.
 * If the memory is not enough, the system will fall
 * */
void obin_memory_start_transaction(ObinState* state);
void obin_memory_end_transaction(ObinState* state);

#define obin_new(state, type) \
		((type*) obin_allocate_cell(state, sizeof(type)))

#define obin_malloc_type(state, type) \
	 ( (type *) obin_malloc(state, sizeof(type)) )

#define obin_malloc_array(state, type, n) \
  ( ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	( (type *) obin_malloc(state, (n) * sizeof(type)) ) )

#define obin_realloc_type(state, p, type, n) \
  ( (p) = ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	(type *) obin_realloc(state, (p), (n) * sizeof(type)) )

#endif
