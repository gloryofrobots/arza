#include <obin.h>
#include "test_memory.h"

static int TMG_VERBOSE = 2;

ObinNativeTraits __TMG_TRAITS__;

#define tmg_print_cell(cell, message) \
	if(TMG_VERBOSE > 1) { \
		printf(message " cell: p=%p id=%d parent_id=%d data_size=%d garbage_size=%d marked_size=%d\n", \
				(void*)cell, cell->id, cell->parent_id, cell->data_size, cell->garbage_size, cell->data_size - cell->garbage_size); }

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t data_size;
	obin_mem_t garbage_size;
	obin_mem_t marked_size;
	int id;
	int parent_id;
	obin_byte* chunk;
	ObinAny* data;
} TMGCell;

static TMCounter* tmg_counter;


ObinAny tmg_cell_new(ObinState* state, int data_size, double garbage_pecentage, int parent_id) {
	TMGCell* cell = obin_new(state, TMGCell);
	int i = 0;

	tm_counter_add(tmg_counter);
	cell->id = tmg_counter->TotalCount;
	cell->parent_id = parent_id;
	cell->chunk = obin_malloc_array(state, obin_byte, 1024);

	cell->data_size = data_size;

	cell->garbage_size = (obin_mem_t) data_size * garbage_pecentage;
	if(cell->garbage_size > cell->data_size) {
			cell->garbage_size = cell->data_size;
	}
	cell->marked_size = cell->data_size - cell->garbage_size;

	tmg_print_cell(cell, "__memory_test_cell_new");

	if(data_size > 0) {

		cell->data = obin_malloc_array(state, ObinAny, data_size);
		for(i=0; i < data_size; i++) {
			cell->data[i] = tmg_cell_new(state, data_size-1, garbage_pecentage, cell->id);

		}
	}

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*) cell, &__TMG_TRAITS__);
}


static void __tmg_cell_mark__(ObinState* state, ObinAny self, obin_proc callback ) {
	int i = 0, count_marked = 0;
	TMGCell* cell = (TMGCell*) obin_any_cell(self);
	TMGCell* child;
	tmg_print_cell(cell, "__test_mem_mark__");
	tm_counter_mark(tmg_counter);

	for(i=0; i<cell->data_size; i++) {
		child = (TMGCell*)obin_any_cell(cell->data[i]);
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

static void __tmg_cell_destroy__(ObinState* state, ObinCell* self) {
	TMGCell* cell = (TMGCell*) self;

	tm_counter_destroy(tmg_counter);

	tmg_print_cell(cell, "__test_mem_destroy__");
	obin_free(state, cell->chunk);
}

ObinBaseTrait __BASE__ = {
	 0,
	 __tmg_cell_destroy__,
	 0, /* clone */
	 0, /*__compare__ */
	 0,/* _hash__ */
	 __tmg_cell_mark__
};

ObinNativeTraits __TMG_TRAITS__ = {
	 "tmg_cell",
	 &__BASE__, /*base*/
	 0, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};

void tmg_test(ObinState* state, obin_mem_t data_size, double garbage_percentage) {
	int old_marked = tmg_counter->Marked,
		destroyed = 0;

	tm_counter_refresh(tmg_counter);

    state->globals = tmg_cell_new(state, data_size, garbage_percentage, tmg_counter->TotalCount);
    printf("Test cells count before collection %d \n", tmg_counter->Count);

    obin_gc_collect(state);

    if(TMG_VERBOSE > 0) {
    	 printf("Test cells count %d \n", tmg_counter->Count);
    	 printf("Test cells count marked %d \n", tmg_counter->Marked);
    	 printf("Test cells destroyed %d \n", tmg_counter->Destroyed);
    }

    destroyed = (tmg_counter->Count -  tmg_counter->Marked) + old_marked;
    CU_ASSERT_EQUAL(destroyed, tmg_counter->Destroyed);
}

static void Test_MemoryGroups(void) {
	tmg_counter = tm_counter_new();
	ObinState * state = obin_state_new(0);
/*	obin_memory_start_transaction(state);*/
	tmg_test(state, 5, 0.5);
	tmg_test(state, 2, 0.5);
	tmg_test(state, 3, 0.5);
	tmg_test(state, 4, 0.5);
	tmg_test(state, 3, 0.4);
	tmg_test(state, 2, 0.2);
	tmg_test(state, 1, 0.4);
	tmg_test(state, 3, 0.3);
	tmg_test(state, 4, 0.4);
	tmg_test(state, 5, 0.2);
	tmg_test(state, 6, 0.8);
	tmg_test(state, 7, 0.7);
/*	tmg_test(state, 8, 0.7);*/

/*	obin_memory_end_transaction(state);*/
	obin_state_destroy(state);
	tm_counter_free(tmg_counter);
}
