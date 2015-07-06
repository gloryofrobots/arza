#include <stdlib.h>
#include <stdio.h>
#include "devutils.h"
#include "obin.h"


ObinNativeTraits __MemoryCell_TRAITS__;

#define __memory_test_print_cell(cell, message) \
		printf(message " cell: id=%d parent_id=%d data_size=%d garbage_size=%d marked_size=%d\n", \
				cell->id, cell->parent_id, cell->data_size, cell->garbage_size, cell->data_size - cell->garbage_size);

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t data_size;
	obin_mem_t garbage_size;
	obin_mem_t marked_size;
	int id;
	int parent_id;
	obin_byte* chunk;
	ObinAny* data;
} __MemoryTestCell;

static int __MemoryTestIdCounter = 0;
static int __MemoryTestTotalMarked = 0;
static int __MemoryTestMarked = 0;
static int __MemoryTestDestroyed = 0;


ObinAny __memory_test_cell_new(ObinState* state, int data_size, double garbage_pecentage, int parent_id) {
	__MemoryTestCell* cell = obin_new(state, __MemoryTestCell);
	int i = 0;

	cell->id = ++__MemoryTestIdCounter;
	cell->parent_id = parent_id;
	cell->chunk = obin_malloc_array(state, obin_byte, 1024);

	cell->data_size = data_size;

	cell->garbage_size = (obin_mem_t) data_size * garbage_pecentage;
	if(cell->garbage_size > cell->data_size) {
			cell->garbage_size = cell->data_size;
	}
	cell->marked_size = cell->data_size - cell->garbage_size;
	__MemoryTestTotalMarked+= cell->marked_size;

	__memory_test_print_cell(cell, "__memory_test_cell_new");

	if(data_size > 0) {

		cell->data = obin_malloc_array(state, ObinAny, data_size);
		for(i=0; i < data_size; i++) {
			cell->data[i] = __memory_test_cell_new(state, data_size-1, garbage_pecentage, cell->id);

		}
	}

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*) cell, &__MemoryCell_TRAITS__);
}


static void __memory_test_cell_mark__(ObinState* state, ObinAny self, obin_proc callback ) {
	int i = 0, count_marked = 0;
	__MemoryTestCell* cell = (__MemoryTestCell*) obin_any_cell(self);
	__MemoryTestCell* child;
	__memory_test_print_cell(cell, "__test_mem_mark__");
	__MemoryTestMarked++;

	for(i=0; i<cell->data_size; i++) {
		child = (__MemoryTestCell*)obin_any_cell(cell->data[i]);
		if(!child->marked_size) {
			continue;
		}
		count_marked++;
		callback(state, cell->data[i]);
		if(count_marked>=cell->marked_size) {
			break;
		}
	}
}

static void __memory_test_cell_destroy__(ObinState* state, ObinCell* self) {
	__MemoryTestCell* cell = (__MemoryTestCell*) self;
	__MemoryTestDestroyed++;
	__memory_test_print_cell(cell, "__test_mem_destroy__");
	obin_free(state, cell->chunk);
}

ObinBaseTrait __BASE__ = {
	 0,
	 __memory_test_cell_destroy__,
	 0, /* clone */
	 0, /*__compare__ */
	 0,/* _hash__ */
	 __memory_test_cell_mark__
};

ObinNativeTraits __MemoryCell_TRAITS__ = {
	 "__memory_test_cell",
	 &__BASE__, /*base*/
	 0, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};


int main() {
	ObinState * state = obin_state_new();
    state->globals = __memory_test_cell_new(state, 2, 0.5, 0);
    obin_gc_collect(state);
    printf("Test cells count %d \n", __MemoryTestIdCounter);
    printf("Test cells count total marked %d \n", __MemoryTestTotalMarked);
    printf("Test cells count marked %d \n", __MemoryTestMarked);
    printf("Test cells destroyed %d \n", __MemoryTestDestroyed);

	obin_state_destroy(state);
	return 0;
}

