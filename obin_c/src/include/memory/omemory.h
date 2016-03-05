#ifndef OBIN_OMEMORY_H_
#define OBIN_OMEMORY_H_
#include "../obuiltin.h"

/*
 * ObinMemoryFreeNode are used to manage the space freed after the sweep phase.
 * these entries contain their own size and a reference of the entry next to them
 */
typedef struct OMemoryFreeNode {
	struct OMemoryFreeNode* next;
    size_t size;
} OMemoryFreeNode;

struct _OMemory {
	void* heap;
	omem_t heap_size;
	omem_t heap_capacity;
	omem_t heap_gc_threshold;
	OMemoryFreeNode* free_node;

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



#define OAny_cellSize(any) (OAny_cellVal(any)->memory.size)

OAny OCell_new(oint typeId, OCell* cell, OBehavior* behavior);

/*TRAITS HERE MUST EXIST IN CELL */
OAny OCell_toAny(OCell* cell);

OState* OState_create(omem_t heap_size);
void OState_destroy(OState* S);

void* omemory_allocate_cell(OState* S, omem_t size);
void omemory_collect(OState* S);

/*TODO REMOVE IT LATER TO statics in c source */
opointer omemory_malloc(OState* S, omem_t size);

opointer omemory_realloc(OState* S, opointer ptr, omem_t size) ;

opointer omemory_memdup(OState* S, opointer ptr, omem_t elements, omem_t element_size );

void omemory_free(OState* S, opointer ptr);

void omemory_debug_trace(OState* S);

/*
 * During memory transactions gc collection will not occur.
 * There are no support for rollbacks now.
 * If the memory is not enough, the system will fall
 * */
void omemory_start_transaction(OState* S);
void omemory_end_transaction(OState* S);

#define obin_new(S, type) \
		((type*) omemory_allocate_cell(S, sizeof(type)))

#define omemory_malloc_type(S, type) \
	 ( (type *) omemory_malloc(S, sizeof(type)) )

#define omemory_malloc_array(S, type, n) \
  ( ((omem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	( (type *) omemory_malloc(S, (n) * sizeof(type)) ) )

#define omemory_realloc_type(S, p, type, n) \
  ( (p) = ((omem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	(type *) omemory_realloc(S, (p), (n) * sizeof(type)) )

#endif
