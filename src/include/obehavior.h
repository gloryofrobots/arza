#ifndef OBEHAVIOR_H_
#define OBEHAVIOR_H_

typedef void (*obin_destructor)(ObinState* state, ObinCell* self);

typedef ObinAny (*obin_func_1)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_func_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_func_3)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3);
typedef ObinAny (*obin_func_4)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3, ObinAny arg4);
typedef ObinAny (*obin_func_1_func_1)(ObinState* state, ObinAny arg, obin_func_1 func);

/*BELOW IS AUTOGEN CODE FROM behavior.py */

typedef struct _ObinBehavior {
    obin_string __name__;
    /*MEMORY*/
    obin_destructor __destroy__;
    obin_func_1_func_1 __mark__;
    /*BASE*/
    obin_func_1 __tostring__;
    obin_func_1 __tobool__;
    obin_func_1 __clone__;
    obin_func_2 __compare__;
    obin_func_1 __hash__;
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


#define OBIN_BEHAVIOR_MEMORY(__destroy__,__mark__)  __destroy__, __mark__

#define OBIN_BEHAVIOR_MEMORY_NULL 0, 0

#define OBIN_BEHAVIOR_BASE(__tostring__,__tobool__,__clone__,__compare__,__hash__)  __tostring__, __tobool__, __clone__, __compare__, __hash__

#define OBIN_BEHAVIOR_BASE_NULL 0, 0, 0, 0, 0

#define OBIN_BEHAVIOR_COLLECTION(__iterator__,__length__,__getitem__,__setitem__,__hasitem__,__delitem__)  __iterator__, __length__, __getitem__, __setitem__, __hasitem__, __delitem__

#define OBIN_BEHAVIOR_COLLECTION_NULL 0, 0, 0, 0, 0, 0

#define OBIN_BEHAVIOR_GENERATOR(__next__)  __next__

#define OBIN_BEHAVIOR_GENERATOR_NULL 0

#define OBIN_BEHAVIOR_NUMBER(__tointeger__,__add__)  __tointeger__, __add__

#define OBIN_BEHAVIOR_NUMBER_NULL 0, 0

#define OBIN_BEHAVIOR_DECLARE(structname) static ObinBehavior structname;

#define OBIN_BEHAVIOR_DEFINE(structname, name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER)  \
static ObinBehavior structname = { \
    name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER  \
};

#endif /* OBEHAVIOR_H_ */
