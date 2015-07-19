#ifndef OCELL_H_
#define OCELL_H_
#include "ostate.h"
#include "memory/ocellmemory.h"

/********************** METHOD POINTERS  ************************************/
typedef void (*obin_destructor)(ObinState* state, ObinCell* self);

typedef ObinAny (*obin_func_1)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_func_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_func_3)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3);
typedef ObinAny (*obin_func_4)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3, ObinAny arg4);
typedef ObinAny (*obin_func_1_func_1)(ObinState* state, ObinAny arg, obin_func_1 func);

typedef struct _ObinBehavior{
	obin_string name;
	obin_destructor __destroy__;
	/*BASE */
	obin_func_1 __tostring__;
	obin_func_1 __tobool__;
	obin_func_1 __clone__;
	obin_func_2 __compare__;
	obin_func_1 __hash__;
	obin_func_1_func_1 __mark__;

	/*COLLECTION*/
	obin_func_1 __iterator__;
	obin_func_1 __length__;
	obin_func_2 __getitem__;
	obin_func_3 __setitem__;
	obin_func_2 __hasitem__;
	obin_func_2 __delitem__;
	/*GENERATOR*/
	obin_func_1 __next__;
	/*NUMBER*/
	obin_func_1 __tointeger__;
	obin_func_2 __add__;
} ObinBehavior;

#define obin_behavior_set(any, method, pointer) obin_any_cell(any)->behavior->method = pointer

/*IT EMPTY FOR NOW*/
#define OBIN_CELL_HEADER \
	ObinBehavior* behavior; \
	ObinCellMemoryInfo memory;

struct _ObinCell {
	OBIN_CELL_HEADER;
};

#define OBIN_DECLARE_CELL(CELLNAME, body) \
typedef struct _##CELLNAME { \
	OBIN_CELL_HEADER \
	body \
} CELLNAME
#endif /* OCELL_H_ */
