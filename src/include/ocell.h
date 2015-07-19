#ifndef OCELL_H_
#define OCELL_H_
#include "ostate.h"
#include "memory/ocellmemory.h"

/********************** NATIVE_TRAIT **************************************/
typedef ObinAny (*obin_function)(ObinAny arg);
typedef ObinAny (*obin_function_2)(ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_function_3)(ObinAny arg1, ObinAny arg2, ObinAny arg3);

typedef void (*obin_proc)(ObinState* state, ObinAny arg);
typedef void (*obin_cell_proc)(ObinState* state, ObinCell* self);
typedef void (*obin_method_2_proc)(ObinState* state, ObinAny arg, obin_proc each);

typedef ObinAny (*obin_method)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_method_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_method_3)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3);

typedef struct {
	obin_method __iterator__;
	obin_method __length__;
	obin_method_2 __getitem__;
	obin_method_3 __setitem__;
	obin_method_2 __hasitem__;
	obin_method_2 __delitem__;
} ObinCollectionTrait;

typedef struct {
	obin_method __next__;
} ObinGeneratorTrait;

typedef struct {
	obin_method __tointeger__;
	obin_method_2 __add__;
} ObinNumberTrait;

typedef struct {
	obin_method __tostring__;
	obin_method __tobool__;
	obin_cell_proc __destroy__;
	obin_method __clone__;
	obin_method_2 __compare__;
	obin_method __hash__;
	obin_method_2_proc __mark__;
} ObinBaseTrait;

typedef struct {
	obin_string name;

	ObinBaseTrait* base;
	ObinCollectionTrait* collection;
	ObinGeneratorTrait* generator;
	ObinNumberTrait* number;
} ObinNativeTraits;


/*IT EMPTY FOR NOW*/
#define OBIN_CELL_HEADER \
	ObinNativeTraits* native_traits; \
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
