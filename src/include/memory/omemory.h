#ifndef OBIN_OMEMORY_H_
#define OBIN_OMEMORY_H_
#include "../obuiltin.h"

/*
 * ObinMemoryFreeNode are used to manage the space freed after the sweep phase.
 * these entries contain their own size and a reference of the entry next to them
 */
typedef struct ObinMemoryFreeNode {
	struct ObinMemoryFreeNode* next;
    size_t size;
} ObinMemoryFreeNode;

struct _OMemory {
	void* heap;
	omem_t heap_size;
	omem_t heap_capacity;
	omem_t heap_gc_threshold;
	ObinMemoryFreeNode* free_node;

	omem_t heap_free_size;
	/*
	 * if this counter equals 0, only then it is safe to collect the
	 * garbage. The counter is increased in cell constructors
	 */
	oint transaction_count; /* the number of collections performed */

	omem_t collections_count; /* the number of collections performed */
	omem_t live_count;        /* number of live objects (per collection) */
	omem_t live_space;        /* space consumed by live objects (per collection) */
	omem_t killed_count;       /* number of freed objects (per collection) */
	omem_t killed_space;       /* freed space (per collection) */
	omem_t allocated_count;       /* number of allocated objects (since last collection) */
	omem_t allocated_space;       /* allocated space (since last collection) */
};



#define obin_any_cell_size(any) (OAny_toCell(any)->memory.size)

OAny obin_cell_new(EOTYPE type, OCell* cell, OBehavior* behavior, OAny root);

/*TRAITS HERE MUST EXIST IN CELL */
OAny obin_cell_to_any(EOTYPE type, OCell* cell);

OState* obin_state_new(omem_t heap_size);
void obin_state_destroy(OState* state);

void* obin_allocate_cell(OState* state, omem_t size);
void obin_gc_collect(OState* state);

/*TODO REMOVE IT LATER TO statics in c source */
opointer obin_memory_malloc(OState* state, omem_t size);

opointer obin_memory_realloc(OState* state, opointer ptr, omem_t size) ;

opointer obin_memory_memdup(OState* state, opointer ptr, omem_t elements, omem_t element_size );

void obin_memory_free(OState* state, opointer ptr);

void obin_memory_debug_trace(OState* state);

/*
 * During memory transactions gc collection will not occur.
 * There are no support for rollbacks now.
 * If the memory is not enough, the system will fall
 * */
void obin_memory_start_transaction(OState* state);
void obin_memory_end_transaction(OState* state);

#define obin_new(state, type) \
		((type*) obin_allocate_cell(state, sizeof(type)))

#define obin_malloc_type(state, type) \
	 ( (type *) obin_malloc(state, sizeof(type)) )

#define obin_malloc_array(state, type, n) \
  ( ((omem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	( (type *) obin_memory_malloc(state, (n) * sizeof(type)) ) )

#define obin_realloc_type(state, p, type, n) \
  ( (p) = ((omem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	(type *) obin_memory_realloc(state, (p), (n) * sizeof(type)) )

#endif
