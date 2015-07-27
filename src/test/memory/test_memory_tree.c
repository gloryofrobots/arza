#include <obin.h>
#include "test_memory.h"

static int TMT_VERBOSE = 0;
static TMCounter* tmt_counter;

/********************* TMT CELL ************************************************/
#define TMTCELL_DATA_SIZE 256
OBEHAVIOR_DECLARE(__TMTCELL_BEHAVIOR__);

OCELL_DECLARE(TMTCell,
	int id;
	OAny left;
	OAny right;
	omem_t size;
	omem_t capacity;
	ochar* data;
);

#define tmtcell(any)   ((TMTCell*) OAny_toCell(any))
#define tmtcell_left(any)   tmtcell(any)->left
#define tmtcell_right(any)  tmtcell(any)->right
#define tmtcell_id(any)   tmtcell(any)->id
#define tmtcell_size(any)   tmtcell(any)->size
#define tmtcell_data(any)   tmtcell(any)->data

void _tmtcell_print(TMTCell* cell, ostring format) {
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


OAny tmtcell_new(OState* S, ostring data, omem_t capacity) {
	TMTCell* cell;
	omem_t size, body_size, data_size;

	body_size = sizeof(TMTCell);
	size = body_size + capacity;

	cell = omemory_allocate_cell(S, size);

	tm_counter_add(tmt_counter);
	cell->id = tmt_counter->TotalCount;
	data_size = strlen(data);
	if(data_size > capacity) {
		opanic("Size of TMTCell data too big");
	}

	cell->data = (ochar*) cell + body_size;
	omemcpy(cell->data, data, data_size);
	cell->capacity = capacity;
	cell->size = data_size;

	tmtcell_print(cell, "tmtcell_new");

	return OCell_new(EOBIN_TYPE_CELL, (OCell*) cell, &__TMTCELL_BEHAVIOR__, ocells(S)->__Cell__);
}


static void __tmtcell_mark__(OState* S, OAny self, ofunc_1 callback ) {
	TMTCell* cell = (TMTCell*) OAny_toCell(self);
	tmtcell_print(cell, "__tmtcell_mark__");
	tm_counter_mark(tmt_counter);

	if(!OAny_isNil(cell->left)) {
		callback(S, cell->left);
	}
	if(!OAny_isNil(cell->right)) {
		callback(S, cell->right);
	}

}

static void __tmtcell_destroy__(OState* S, OCell* self) {
	TMTCell* cell = (TMTCell*) self;
	tm_counter_destroy(tmt_counter);
	tmtcell_print(cell, "__tmtcell_destroy__");
}

OBEHAVIOR_DEFINE(__TMTCELL_BEHAVIOR__,
		"tmtcell",
		OBEHAVIOR_MEMORY(__tmtcell_destroy__, __tmtcell_mark__),
		OBEHAVIOR_BASE_NULL,
		OBEHAVIOR_COLLECTION_NULL,
		OBEHAVIOR_GENERATOR_NULL,
		OBEHAVIOR_NUMBER_CAST_NULL,
		OBEHAVIOR_NUMBER_OPERATIONS_NULL
);

typedef struct _TMTTestRequests {
	oint live_count;
	oint live_space;
	oint killed_count;
	oint killed_space;
	oint allocated_count;
	oint allocated_space;
} _TMTTestStat;

_TMTTestStat tmt_stat_new(obool live, obool killed, obool allocated) {
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
OAny tmt_stat_add_cell(_TMTTestStat* requests, OAny node, obool is_alive) {
	if(is_alive) {
        requests->live_count++;
        requests->live_space += OAny_cellSize(node);
	} else {
        requests->killed_count++;
        requests->killed_space += OAny_cellSize(node);
	}
	requests->allocated_count++;
	requests->allocated_space  += OAny_cellSize(node);

	return node;
}

OAny tmt_stat_create_cell(_TMTTestStat* requests, obool is_alive, OState* S,  ostring data, omem_t capacity) {
	OAny node = tmtcell_new(S, data, capacity);
	return tmt_stat_add_cell(requests, node, is_alive);
}


_TMTTestStat _test1(OState* S) {
	OAny root;
	_TMTTestStat requests = tmt_stat_new(OTRUE, OTRUE, OTRUE);

    root = tmt_stat_create_cell(&requests, OTRUE, S, "RootNode", 192);
    S->globals = root;
    tmtcell_left(root) = tmt_stat_create_cell(&requests, OTRUE, S, "RootLeft", 192);
	tmtcell_right(root) = tmt_stat_create_cell(&requests, OTRUE,S, "RootRight", 192);

	tmt_stat_create_cell(&requests, OFALSE, S, "DeadNode1", 128);


	return requests;
}
_TMTTestStat _test2(OState* S) {
	OAny leftnode, rightnode, node, node2;
	_TMTTestStat requests = tmt_stat_new(OTRUE, OTRUE, OTRUE);

	node = tmt_stat_create_cell(&requests, OTRUE, S, "R", 10);
    S->globals = node;
    tmtcell_left(node) = tmt_stat_create_cell(&requests, OTRUE, S, "L1", 20);
	tmtcell_right(node) = tmt_stat_create_cell(&requests, OTRUE,S, "R1", 14);

	leftnode = tmtcell_left(node);
	tmtcell_left(leftnode) = tmt_stat_create_cell(&requests, OTRUE, S, "L2", 20);
	tmtcell_right(leftnode) = ObinNil;

	rightnode = tmtcell_right(node);
	node2 = rightnode;
	tmtcell_left(rightnode) = tmt_stat_create_cell(&requests, OTRUE, S, "L3", 20);
	/*dead branch */
	tmtcell_right(rightnode) = tmt_stat_create_cell(&requests, OFALSE,S, "R3", 14);
	node = tmtcell_right(rightnode);
	tmtcell_left(node) = tmt_stat_create_cell(&requests, OFALSE, S, "L4", 20);
	tmtcell_right(node) = tmt_stat_create_cell(&requests, OFALSE,S, "R4", 14);

	leftnode = tmtcell_left(node);
	tmtcell_left(leftnode) = tmt_stat_create_cell(&requests, OFALSE, S, "L5", 20);
	tmtcell_right(leftnode) =  tmt_stat_create_cell(&requests, OFALSE, S, "R5", 20);

	rightnode = tmtcell_right(node);
	/* it will live */
	tmtcell_left(rightnode) = tmt_stat_create_cell(&requests, OTRUE, S, "L6", 20);
	tmtcell_right(node2) = tmtcell_left(rightnode);

	tmtcell_right(rightnode) = tmt_stat_create_cell(&requests, OFALSE,S, "R6", 14);

	return requests;
}

void _test_clear(OState* S, _TMTTestStat stat) {
	S->globals = ObinNil;
	omemory_collect(S);

    CU_ASSERT_EQUAL(S->memory->allocated_count, 0);
	CU_ASSERT_EQUAL(S->memory->allocated_space, 0);
	CU_ASSERT_EQUAL(S->memory->heap_free_size, S->memory->heap_size - S->memory->allocated_space);
	CU_ASSERT_EQUAL(S->memory->live_count, 0);
	CU_ASSERT_EQUAL(S->memory->live_space, 0);
	CU_ASSERT_EQUAL(S->memory->killed_count, stat.live_count);
	CU_ASSERT_EQUAL(S->memory->killed_space, stat.live_space);
}

typedef _TMTTestStat (*__tmt_test)(OState* );
/******************** TEST *****************/
_TMTTestStat _tmt_make_test(OState* S, __tmt_test test) {
	int destroyed = 0;
	_TMTTestStat requests;

	tm_counter_refresh(tmt_counter);

	requests = test(S);

    printf("Test cells count before collection %d \n", tmt_counter->Count);

    if(requests.allocated_count > -1) {
    	CU_ASSERT_EQUAL(S->memory->allocated_count, requests.allocated_count);
    }
    if(requests.allocated_space > -1) {
    	CU_ASSERT_EQUAL(S->memory->allocated_space, requests.allocated_space);
    	CU_ASSERT_EQUAL(S->memory->heap_free_size, S->memory->heap_size - S->memory->allocated_space);
    }

    omemory_collect(S);


    if(TMT_VERBOSE > 0) {
    	tm_counter_info(tmt_counter);
    	omemory_debug_trace(S);
    }

    if(requests.live_count > -1) {
    	CU_ASSERT_EQUAL(S->memory->live_count, requests.live_count);
    }
    if(requests.live_space > -1) {
    	CU_ASSERT_EQUAL(S->memory->live_space, requests.live_space);
    }
    if(requests.killed_count > -1) {
    	CU_ASSERT_EQUAL(S->memory->killed_count, requests.killed_count);
    }
    if(requests.killed_space > -1) {
    	CU_ASSERT_EQUAL(S->memory->killed_space, requests.killed_space);
    }

    destroyed = tm_counter_predict_destroyed(tmt_counter);
    CU_ASSERT_EQUAL(destroyed, tmt_counter->Destroyed);

    return requests;
}

void tmt_test() {
	_TMTTestStat stat;
	tmt_counter = tm_counter_new();
	OState * S;
    int heap_size  = 2048;

	S = obin_init(heap_size);

	stat = _tmt_make_test(S, _test1);
	_test_clear(S, stat);
	stat = _tmt_make_test(S, _test2);
	_test_clear(S, stat);

	OState_destroy(S);
	tm_counter_free(tmt_counter);
}

static void Test_MemoryTree(void) {
/*	printf("\n---%d\n", sizeof(ObinCell));
	printf("---%d\n", sizeof(TMTCell));*/
	tmt_test();
}
