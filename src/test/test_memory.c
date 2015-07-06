ObinNativeTraits __MemoryCell_TRAITS__;

typedef struct {
	OBIN_CELL_HEADER;
	obin_mem_t data_size;
	obin_mem_t garbage_size;
	int id;

	obin_byte* chunk;
	ObinAny* data;
} __MemoryTestCell;

static int __MemoryTestIdCounter = 0;

ObinAny __memory_test_cell_new(ObinState* state, int data_size, int garbage_size) {
	__MemoryTestCell* cell = obin_new(state, __MemoryTestCell);
	int i = 0;

	cell->id = ++__MemoryTestIdCounter;
	cell->chunk = obin_malloc_array(state, obin_byte, 1024);

	if(data_size > 0) {
		cell->garbage_size = garbage_size > 0 ? garbage_size : 0;

		cell->data_size = data_size;
		cell->data = obin_malloc_array(state, ObinAny, data_size);
		for(i=0; i < data_size; i++) {
			cell->data[i] = __memory_test_cell_new(state, data_size-1, garbage_size - 1);
		}
	}

	return obin_cell_new(EOBIN_TYPE_OBJECT, (ObinCell*) cell, &__MemoryCell_TRAITS__);
}

#define __memory_test_print_cell(cell, message) \
		printf(message " cell: id = %d data_size=%d garbage_size=%d marked_size=%d\n", \
				cell->id, cell->data_size, cell->garbage_size, cell->data_size - cell->garbage_size);

static void __memory_test_cell_mark__(ObinState* state, ObinAny self, obin_proc callback ) {
	int i = 0;
	__MemoryTestCell* cell = (__MemoryTestCell*) obin_any_cell(self);
	int marked_size = cell->data_size - cell->garbage_size;

	__memory_test_print_cell(cell, "__test_mem_mark__");

	for(i=0; i < marked_size; i++) {
		callback(state, cell->data[i]);
	}
}

static void __memory_test_cell_destroy__(ObinState* state, ObinCell* self) {
	__MemoryTestCell* cell = (__MemoryTestCell*) self;

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


static void Test_Memory(void) {
	ObinState * state = obin_state_new();
	ObinAny test_cell = __memory_test_cell_new(state, 2, 1);

	obin_state_destroy(state);
}
static CU_TestInfo TestGroup_Memory[] = {
  { "Test_BaseTypes", Test_Memory },
	CU_TEST_INFO_NULL,
};
