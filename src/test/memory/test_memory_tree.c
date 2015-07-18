#include <obin.h>
#include "test_memory.h"

static int TMT_VERBOSE = 0;
static TMCounter* tmt_counter;

/********************* TMT CELL ************************************************/
#define TMTCELL_DATA_SIZE 256
ObinNativeTraits __TMTCELL_TRAITS__;

OBIN_DECLARE_CELL(TMTCell,
	int id;
	ObinAny left;
	ObinAny right;
	obin_mem_t size;
	obin_mem_t capacity;
	obin_char* data;
);

#define tmtcell(any)   ((TMTCell*) obin_any_cell(any))
#define tmtcell_left(any)   tmtcell(any)->left
#define tmtcell_right(any)  tmtcell(any)->right
#define tmtcell_id(any)   tmtcell(any)->id
#define tmtcell_size(any)   tmtcell(any)->size
#define tmtcell_data(any)   tmtcell(any)->data

void _tmtcell_print(TMTCell* cell, obin_string format) {
	if(TMT_VERBOSE > 1) {
		printf(format,
				cell->id, cell->data);
	}
/*	if(!obin_any_is_nil(cell->left)) {
		printf("left: \n");
		_tmtcell_print(tmtcell(cell->left), format);
	}
	if(!obin_any_is_nil(cell->right)) {
		printf("right: \n");
		_tmtcell_print(tmtcell(cell->right), format);
	}*/
}

#define tmtcell_print(cell, message) \
		_tmtcell_print(cell, message " cell: id=%d  data=%s \n")


ObinAny tmtcell_new(ObinState* state, obin_string data, obin_mem_t capacity) {
	TMTCell* cell;
	obin_mem_t size, body_size, data_size;

	body_size = sizeof(TMTCell);
	size = body_size + capacity;

	cell = obin_allocate_cell(state, size);

	tm_counter_add(tmt_counter);
	cell->id = tmt_counter->TotalCount;
	data_size = strlen(data);
	if(data_size > capacity) {
		obin_panic("Size of TMTCell data too big");
	}

	cell->data = (obin_char*) cell + body_size;
	obin_memcpy(cell->data, data, data_size);
	cell->capacity = capacity;
	cell->size = data_size;

	tmtcell_print(cell, "tmtcell_new");

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*) cell, &__TMTCELL_TRAITS__);
}


static void __tmtcell_mark__(ObinState* state, ObinAny self, obin_proc callback ) {
	TMTCell* cell = (TMTCell*) obin_any_cell(self);
	tmtcell_print(cell, "__tmtcell_mark__");
	tm_counter_mark(tmt_counter);

	if(!obin_any_is_nil(cell->left)) {
		callback(state, cell->left);
	}
	if(!obin_any_is_nil(cell->right)) {
		callback(state, cell->right);
	}

}

static void __tmtcell_destroy__(ObinState* state, ObinCell* self) {
	TMTCell* cell = (TMTCell*) self;
	tm_counter_destroy(tmt_counter);
	tmtcell_print(cell, "__tmtcell_destroy__");
}

ObinBaseTrait __TMTCELL_BASE__ = {
	 0,
	 0,
	 __tmtcell_destroy__,
	 0, /* clone */
	 0, /*__compare__ */
	 0,/* _hash__ */
	 __tmtcell_mark__
};

ObinNativeTraits __TMTCELL_TRAITS__ = {
	 "tmtcell",
	 &__TMTCELL_BASE__, /*base*/
	 0, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};

typedef struct _TMTTestRequests {
	obin_integer live_count;
	obin_integer live_space;
	obin_integer killed_count;
	obin_integer killed_space;
	obin_integer allocated_count;
	obin_integer allocated_space;
} _TMTTestStat;

_TMTTestStat tmt_stat_new(obin_bool live, obin_bool killed, obin_bool allocated) {
	_TMTTestStat stat = {0};
	if(!live) {
		stat.live_count = -1;
		stat.live_space = -1;
	}
	if(!killed) {
		stat.killed_count = -1;
		stat.killed_space = -1;
	}
	if(!allocated) {
		stat.allocated_count = -1;
		stat.allocated_space = -1;
	}
	return stat;
}
ObinAny tmt_stat_add_cell(_TMTTestStat* requests, ObinAny node, obin_bool is_alive) {
	if(is_alive) {
        requests->live_count++;
        requests->live_space += obin_any_cell_size(node);
	} else {
        requests->killed_count++;
        requests->killed_space += obin_any_cell_size(node);
	}
	requests->allocated_count++;
	requests->allocated_space  += obin_any_cell_size(node);

	return node;
}

ObinAny tmt_stat_create_cell(_TMTTestStat* requests, obin_bool is_alive, ObinState* state,  obin_string data, obin_mem_t capacity) {
	ObinAny node = tmtcell_new(state, data, capacity);
	return tmt_stat_add_cell(requests, node, is_alive);
}


_TMTTestStat _test1(ObinState* state) {
	ObinAny root;
	_TMTTestStat requests = tmt_stat_new(OTRUE, OTRUE, OTRUE);

    root = tmt_stat_create_cell(&requests, OTRUE, state, "RootNode", 192);
    state->globals = root;
    tmtcell_left(root) = tmt_stat_create_cell(&requests, OTRUE, state, "RootLeft", 192);
	tmtcell_right(root) = tmt_stat_create_cell(&requests, OTRUE,state, "RootRight", 192);

	tmt_stat_create_cell(&requests, OFALSE, state, "DeadNode1", 128);


	return requests;
}
_TMTTestStat _test2(ObinState* state) {
	ObinAny leftnode, rightnode, node, node2;
	_TMTTestStat requests = tmt_stat_new(OTRUE, OTRUE, OTRUE);

	node = tmt_stat_create_cell(&requests, OTRUE, state, "R", 10);
    state->globals = node;
    tmtcell_left(node) = tmt_stat_create_cell(&requests, OTRUE, state, "L1", 20);
	tmtcell_right(node) = tmt_stat_create_cell(&requests, OTRUE,state, "R1", 14);

	leftnode = tmtcell_left(node);
	tmtcell_left(leftnode) = tmt_stat_create_cell(&requests, OTRUE, state, "L2", 20);
	tmtcell_right(leftnode) = ObinNil;

	rightnode = tmtcell_right(node);
	node2 = rightnode;
	tmtcell_left(rightnode) = tmt_stat_create_cell(&requests, OTRUE, state, "L3", 20);
	/*dead branch */
	tmtcell_right(rightnode) = tmt_stat_create_cell(&requests, OFALSE,state, "R3", 14);
	node = tmtcell_right(rightnode);
	tmtcell_left(node) = tmt_stat_create_cell(&requests, OFALSE, state, "L4", 20);
	tmtcell_right(node) = tmt_stat_create_cell(&requests, OFALSE,state, "R4", 14);

	leftnode = tmtcell_left(node);
	tmtcell_left(leftnode) = tmt_stat_create_cell(&requests, OFALSE, state, "L5", 20);
	tmtcell_right(leftnode) =  tmt_stat_create_cell(&requests, OFALSE, state, "R5", 20);

	rightnode = tmtcell_right(node);
	/* it will live */
	tmtcell_left(rightnode) = tmt_stat_create_cell(&requests, OTRUE, state, "L6", 20);
	tmtcell_right(node2) = tmtcell_left(rightnode);

	tmtcell_right(rightnode) = tmt_stat_create_cell(&requests, OFALSE,state, "R6", 14);

	return requests;
}

void _test_clear(ObinState* state, _TMTTestStat stat) {
	state->globals = ObinNil;
	obin_gc_collect(state);

    CU_ASSERT_EQUAL(state->memory->allocated_count, 0);
	CU_ASSERT_EQUAL(state->memory->allocated_space, 0);
	CU_ASSERT_EQUAL(state->memory->heap_free_size, state->memory->heap_size - state->memory->allocated_space);
	CU_ASSERT_EQUAL(state->memory->live_count, 0);
	CU_ASSERT_EQUAL(state->memory->live_space, 0);
	CU_ASSERT_EQUAL(state->memory->killed_count, stat.live_count);
	CU_ASSERT_EQUAL(state->memory->killed_space, stat.live_space);
}

typedef _TMTTestStat (*__tmt_test)(ObinState* );
/******************** TEST *****************/
_TMTTestStat _tmt_make_test(ObinState* state, __tmt_test test) {
	int destroyed = 0;
	_TMTTestStat requests;

	tm_counter_refresh(tmt_counter);

	requests = test(state);

    printf("Test cells count before collection %d \n", tmt_counter->Count);

    if(requests.allocated_count > -1) {
    	CU_ASSERT_EQUAL(state->memory->allocated_count, requests.allocated_count);
    }
    if(requests.allocated_space > -1) {
    	CU_ASSERT_EQUAL(state->memory->allocated_space, requests.allocated_space);
    	CU_ASSERT_EQUAL(state->memory->heap_free_size, state->memory->heap_size - state->memory->allocated_space);
    }

    obin_gc_collect(state);


    if(TMT_VERBOSE > 0) {
    	tm_counter_info(tmt_counter);
    	obin_memory_debug_trace(state);
    }

    if(requests.live_count > -1) {
    	CU_ASSERT_EQUAL(state->memory->live_count, requests.live_count);
    }
    if(requests.live_space > -1) {
    	CU_ASSERT_EQUAL(state->memory->live_space, requests.live_space);
    }
    if(requests.killed_count > -1) {
    	CU_ASSERT_EQUAL(state->memory->killed_count, requests.killed_count);
    }
    if(requests.killed_space > -1) {
    	CU_ASSERT_EQUAL(state->memory->killed_space, requests.killed_space);
    }

    destroyed = tm_counter_predict_destroyed(tmt_counter);
    CU_ASSERT_EQUAL(destroyed, tmt_counter->Destroyed);

    return requests;
}

void tmt_test() {
	_TMTTestStat stat;
	tmt_counter = tm_counter_new();
	ObinState * state;
    int heap_size  = 1024;

	state = obin_init(heap_size);

	stat = _tmt_make_test(state, _test1);
	_test_clear(state, stat);
	stat = _tmt_make_test(state, _test2);
	_test_clear(state, stat);

	obin_state_destroy(state);
	tm_counter_free(tmt_counter);
}

static void Test_MemoryTree(void) {
	tmt_test();
}
