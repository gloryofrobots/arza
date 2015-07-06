#ifndef OBIN_OMEMORY_H_
#define OBIN_OMEMORY_H_
#include "obuiltin.h"

/*
 * free_list_entries are used to manage the space freed after the sweep phase.
 * these entries contain their own size and a reference of the entry next to them
 */
typedef struct free_list_entry {
	struct free_list_entry* next;
    size_t size;
} free_list_entry;

int BUFFERSIZE_FOR_UNINTERRUPTABLE = 50000;
int OBJECT_SPACE_SIZE = 1048576;

struct _ObinMemory {
	void* object_space;
	int OBJECT_SPACE_SIZE;
	int BUFFERSIZE_FOR_UNINTERRUPTABLE;
	free_list_entry* first_free_entry;
        /*
         * if this counter equals 0, only then it is safe to collect the
         * garbage. The counter is increased during initializations of
         * VMObjects and the generation of classes
         */
    int uninterruptable_counter;

    int size_of_free_heap;

	uint32_t num_collections; /* the number of collections performed */
	uint32_t num_live;        /* number of live objects (per collection) */
	uint32_t spc_live;        /* space consumed by live objects (per collection) */
	uint32_t num_freed;       /* number of freed objects (per collection) */
	uint32_t spc_freed;       /* freed space (per collection) */
	uint32_t num_alloc;       /* number of allocated objects (since last collection) */
	uint32_t spc_alloc;       /* allocated space (since last collection) */
};

typedef struct{
	obin_integer lives;
	obin_integer deads;
	obin_integer rc;

	obin_bool mark;
	obin_mem_t size;
} ObinCellMemoryInfo;

/*IT EMPTY FOR NOW */
#define OBIN_CELL_HEADER \
	ObinNativeTraits* native_traits; \
	ObinCellMemoryInfo memory;

struct _ObinCell {
	OBIN_CELL_HEADER;
};

static ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell, ObinNativeTraits* traits) {
	ObinAny result;
	obin_assert(obin_type_is_cell(type));

	cell->native_traits = traits;

	result = obin_any_new();
	obin_any_init_cell(result, type, cell);
	return result;
}

void obin_memory_create(ObinState* state, obin_mem_t heap_size);
void obin_memory_destroy(ObinState* state);

void* obin_allocate_cell(ObinState* state, obin_mem_t size);

obin_pointer obin_malloc(ObinState* state, obin_mem_t size);

obin_pointer obin_realloc(ObinState* state, obin_pointer ptr, obin_mem_t size) ;

obin_pointer obin_memdup(ObinState* state, obin_pointer ptr, obin_mem_t elements, obin_mem_t element_size );

void obin_free(ObinState* state, obin_pointer ptr);

/*Reference counter */
ObinAny obin_hold(ObinState* state, ObinAny any);
ObinAny obin_release(ObinState* state, ObinAny any);


#define obin_sincref(state, any) \
	(obin_any_is_cell(any) ? obin_incref(any) : any)

#define obin_sdecref(state, any) \
	(obin_any_is_cell(any) ? obin_decref(any) : any)


#define obin_new(state, type) \
		((type*) obin_allocate_cell(state, sizeof(type))

#define obin_malloc_type(state, type) \
	 ( (type *) obin_malloc(state, sizeof(type)) )

#define obin_malloc_array(state, type, n) \
  ( ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	( (type *) obin_malloc(state, (n) * sizeof(type)) ) )

#define obin_realloc_type(state, p, type, n) \
  ( (p) = ((obin_mem_t)(n) > OBIN_MEM_MAX / sizeof(type)) ? NULL :	\
	(type *) obin_realloc(state, (p), (n) * sizeof(type)) )



/*void gc_start_uninterruptable_allocation();
void gc_end_uninterruptable_allocation();*/
#endif
