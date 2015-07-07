#include <obin.h>
#include "test_memory.h"

static int TMT_VERBOSE = 2;
static TMCounter* tmt_counter;

/********************* TMT CELL ************************************************/
#define TMTCELL_DATA_SIZE 256
ObinNativeTraits __TMTCELL_TRAITS__;

typedef struct {
	OBIN_CELL_HEADER;
	obin_char data[TMTCELL_DATA_SIZE];
	obin_mem_t size;

	int id;
	ObinAny left;
	ObinAny right;
	ObinAny root;
} TMTCell;

#define tmtcell(any)   ((TMTCell*) obin_any_cell(any))
#define tmtcell_left(any)   tmtcell(any)->left
#define tmtcell_right(any)  tmtcell(any)->right
#define tmtcell_root(any)   tmtcell(any)->root
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


ObinAny tmtcell_new(ObinState* state, obin_string data, ObinAny root) {
	TMTCell* cell = obin_new(state, TMTCell);
	obin_mem_t size;

	tm_counter_add(tmt_counter);

	cell->id = tmt_counter->TotalCount;
	size = strlen(data);
	if(size > TMTCELL_DATA_SIZE) {
		obin_panic("Size of TMTCell data too big");
	}

	obin_memcpy(cell->data, data, size);
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


/************************************ FAT CELL **************************************/

ObinNativeTraits __TMTFATCELL_TRAITS__;
#define TMTFATCELL_DATA_SIZE 1024
typedef struct {
	OBIN_CELL_HEADER;
	obin_char data[TMTFATCELL_DATA_SIZE];
	obin_mem_t size;
	int id;
} TMTFatCell;


#define tmtfatcell(any)   ((TMTFatCell*) obin_any_cell(any))
#define tmtfatcell_data(any)   tmtfatcell(any)->data
#define tmtfatcell_id(any)   tmtfatcell(any)->id
#define tmtfatcell_size(any)   tmtfatcell(any)->size

void _tmtfatcell_print(TMTFatCell* cell, obin_string format) {
	if(TMT_VERBOSE > 1) {
		printf(format,
				cell->id, cell->data);
	}
}

#define tmtfatcell_print(cell, message) \
		_tmtfatcell_print(cell, message " cell: id=%d  data=%s \n")


ObinAny tmtfatcell_new(ObinState* state, obin_string data, ObinAny root) {
	TMTFatCell* cell = obin_new(state, TMTFatCell);
	obin_mem_t size;

	tm_counter_add(tmt_counter);

	cell->id = tmt_counter->TotalCount;
	size = strlen(data);
	if(size > TMTFATCELL_DATA_SIZE) {
		obin_panic("Size of TMTFatCell data too big");
	}

	obin_memcpy(cell->data, data, size);
	tmtfatcell_print(cell, "tmtfatcell_new");

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*) cell, &__TMTFATCELL_TRAITS__);
}

static void __tmtfatcell_mark__(ObinState* state, ObinAny self, obin_proc callback ) {
	TMTFatCell* cell = (TMTFatCell*) obin_any_cell(self);
	tmtfatcell_print(cell, "__tmtfatcell_mark__");
	tm_counter_mark(tmt_counter);
}

static void __tmtfatcell_destroy__(ObinState* state, ObinCell* self) {
	TMTFatCell* cell = (TMTFatCell*) self;
	tm_counter_destroy(tmt_counter);
	tmtfatcell_print(cell, "__tmtfatcell_destroy__");
}

ObinBaseTrait __TMTFATCELL_BASE__ = {
	 0,
	 __tmtfatcell_destroy__,
	 0, /* clone */
	 0, /*__compare__ */
	 0,/* _hash__ */
	 __tmtfatcell_mark__
};

ObinNativeTraits __TMTFATCELL_TRAITS__ = {
	 "tmtcell",
	 &__TMTFATCELL_BASE__, /*base*/
	 0, /*collection*/
	 0, /*generator*/
	 0, /*number*/
};

/******************** TEST *****************/
void _tmt_test(ObinState* state) {
	int destroyed = 0;
	int i = 0;
	ObinAny root;

	tm_counter_refresh(tmt_counter);

    root = tmtcell_new(state, "RootNode", ObinNil);
    state->globals = root;
    tmtcell_left(root) = tmtcell_new(state, "RootLeft", ObinNil);
	tmtfatcell_new(state, "KamikadzeNode", ObinNil);
	tmtcell_right(root) = tmtfatcell_new(state, "RootRight", ObinNil);

    for(i = 0; i < 10; i++) {
    	tmtcell_right(root) = tmtfatcell_new(state, "KillerNode", ObinNil);
    }
    printf("Test cells count before collection %d \n", tmt_counter->Count);

    obin_gc_collect(state);

    if(TMT_VERBOSE > 0) {
    	tm_counter_info(tmt_counter);
    }

    destroyed = tm_counter_predict_destroyed(tmt_counter);
    CU_ASSERT_EQUAL(destroyed, tmt_counter->Destroyed);
}

void tmt_test() {
	tmt_counter = tm_counter_new();
	ObinState * state;
    int heap_size  = 1024*2;

	state = obin_state_new(heap_size);

	_tmt_test(state);

	obin_state_destroy(state);
	tm_counter_free(tmt_counter);
}

static void Test_MemoryTree(void) {
	tmt_test();
}
