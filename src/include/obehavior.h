#ifndef OBEHAVIOR_H_
#define OBEHAVIOR_H_

typedef void (*obin_destructor)(ObinState* state, ObinCell* self);

typedef ObinAny (*obin_func_1)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_func_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_func_3)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3);
typedef ObinAny (*obin_func_4)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3, ObinAny arg4);
typedef ObinAny (*obin_func_1_func_1)(ObinState* state, ObinAny arg, obin_func_1 func);

typedef struct _ObinBehavior{
	obin_string __name__;
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


#endif /* OBEHAVIOR_H_ */
