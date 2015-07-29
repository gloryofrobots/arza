#include <obin.h>
#include "test_memory.h"

static int TMG_VERBOSE = 0;

OBEHAVIOR_DECLARE(__TMGCELL_BEHAVIOR__);

#define tmg_print_cell(cell, message) \
	if(TMG_VERBOSE > 1) { \
		printf(message " cell: p=%p id=%d parent_id=%d data_size=%d garbage_size=%d marked_size=%d\n", \
				(void*)cell, cell->id, cell->parent_id, cell->data_size, cell->garbage_size, cell->data_size - cell->garbage_size); }

typedef struct {
	OCELL_HEADER;
	omem_t data_size;
	omem_t garbage_size;
	omem_t marked_size;
	int id;
	int parent_id;
	obyte* chunk;
	OAny* data;
} TMGCell;

static TMCounter* tmg_counter;


OAny tmg_cell_new(OState* S, int data_size, double garbage_pecentage, int parent_id) {
	TMGCell* cell = obin_new(S, TMGCell);
	int i = 0;

	tm_counter_add(tmg_counter);
	cell->id = tmg_counter->TotalCount;
	cell->parent_id = parent_id;
	cell->chunk = omemory_malloc_array(S, obyte, 1024);

	cell->data_size = data_size;

	cell->garbage_size = (omem_t) data_size * garbage_pecentage;
	if(cell->garbage_size > cell->data_size) {
			cell->garbage_size = cell->data_size;
	}
	cell->marked_size = cell->data_size - cell->garbage_size;

	tmg_print_cell(cell, "__memory_test_cell_new");

	if(data_size > 0) {

		cell->data = omemory_malloc_array(S, OAny, data_size);
		for(i=0; i < data_size; i++) {
			cell->data[i] = tmg_cell_new(S, data_size-1, garbage_pecentage, cell->id);

		}
	}

	return OCell_new(EOBIN_TYPE_CELL, (OCell*) cell, &__TMGCELL_BEHAVIOR__, ocells(S)->__Cell__);
}


static void __tmg_cell_mark__(OState* S, OAny self, ofunc_1 callback ) {
	int i = 0, count_marked = 0;
	TMGCell* cell = (TMGCell*) OAny_cellVal(self);
	TMGCell* child;
	tmg_print_cell(cell, "__test_mem_mark__");
	tm_counter_mark(tmg_counter);

	for(i=0; i<cell->data_size; i++) {
		child = (TMGCell*)OAny_cellVal(cell->data[i]);
		if(!child->marked_size) {
			continue;
		}
		count_marked++;
		callback(S, cell->data[i]);
		if(count_marked>=cell->marked_size) {
			break;
		}
	}
}

static void __tmg_cell_destroy__(OState* S, OCell* self) {
	TMGCell* cell = (TMGCell*) self;

	tm_counter_destroy(tmg_counter);

	tmg_print_cell(cell, "__test_mem_destroy__");
	omemory_free(S, cell->chunk);
}

OBEHAVIOR_DEFINE(__TMGCELL_BEHAVIOR__,
		"tmgcell",
		OBEHAVIOR_MEMORY(__tmg_cell_destroy__, __tmg_cell_mark__),
		OBEHAVIOR_BASE_NULL,
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR_NULL,
		OBEHAVIOR_NUMBER_NULL
);

void tmg_test(OState* S, omem_t data_size, double garbage_percentage) {
	int destroyed = 0;
	if(TMG_VERBOSE > 0) {
		printf("\ntmg_test data_size:%d garbage_percentage:%.2f\n", data_size, garbage_percentage);
	}
/*    obin_memory_debug_trace(S);*/

	tm_counter_remember(tmg_counter);
	tm_counter_refresh(tmg_counter);

    S->globals = tmg_cell_new(S, data_size, garbage_percentage, tmg_counter->TotalCount);
	if(TMG_VERBOSE > 0) {
		printf("Test cells count before collection %d \n", tmg_counter->Count);
	}
    omemory_collect(S);
    destroyed = tm_counter_predict_destroyed(tmg_counter);

    if(TMG_VERBOSE > 0) {
    	tm_counter_info(tmg_counter);
    	omemory_debug_trace(S);
    }

    CU_ASSERT_EQUAL(destroyed, tmg_counter->Destroyed);
}

static void Test_MemoryGroups(void) {
	tmg_counter = tm_counter_new();
	OState * S = obin_init(1024 * 1024 * 90);
/*	obin_memory_start_transaction(S);*/
	tmg_test(S, 5, 0.5);
	tmg_test(S, 2, 0.5);
	tmg_test(S, 3, 0.5);
	tmg_test(S, 4, 0.5);
	tmg_test(S, 3, 0.4);
	tmg_test(S, 2, 0.2);
	tmg_test(S, 1, 0.4);
	tmg_test(S, 3, 0.3);
	tmg_test(S, 4, 0.4);
	tmg_test(S, 5, 0.2);
	tmg_test(S, 6, 0.8);
	tmg_test(S, 7, 0.7);
	tmg_test(S, 2, 0.7);
	/*tmg_test(S, 9, 0.7);*/

/*	obin_memory_end_transaction(S);*/
	OState_destroy(S);
	tm_counter_free(tmg_counter);
}
