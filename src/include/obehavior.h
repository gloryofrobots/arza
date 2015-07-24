#ifndef OBEHAVIOR_H_
#define OBEHAVIOR_H_

typedef void (*obin_destructor)(ObinState* state, OCell* self);

typedef OAny (*obin_func_1)(ObinState* state, OAny arg);
typedef OAny (*obin_func_2)(ObinState* state, OAny arg1, OAny arg2);
typedef OAny (*obin_func_3)(ObinState* state, OAny arg1, OAny arg2, OAny arg3);
typedef OAny (*obin_func_4)(ObinState* state, OAny arg1, OAny arg2, OAny arg3, OAny arg4);
typedef void (*obin_each)(ObinState* state, OAny arg, obin_func_1 func);

/*BELOW IS AUTOGEN CODE FROM behavior.py */

typedef struct _ObinBehavior {
    obin_string __name__;
    /*MEMORY*/
    obin_destructor __destroy__;
    obin_each __mark__;
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
    /*NUMBER_CAST*/
    obin_func_1 __tointeger__;
    obin_func_1 __tofloat__;
    obin_func_1 __topositive__;
    obin_func_1 __tonegative__;
    /*NUMBER_OPERATIONS*/
    obin_func_1 __abs__;
    obin_func_1 __invert__;
    obin_func_2 __add__;
    obin_func_2 __subtract__;
    obin_func_2 __divide__;
    obin_func_2 __multiply__;
    obin_func_2 __pow__;
    obin_func_2 __leftshift__;
    obin_func_2 __rightshift__;
    obin_func_2 __mod__;
    obin_func_2 __and__;
    obin_func_2 __or__;
    obin_func_2 __xor__;

} ObinBehavior;

#define OBIN_BEHAVIOR_MEMORY(__destroy__,__mark__)  __destroy__, __mark__

#define OBIN_BEHAVIOR_MEMORY_NULL 0, 0
#define OBIN_BEHAVIOR_BASE(__tostring__,__tobool__,__clone__,__compare__,__hash__)  __tostring__, __tobool__, __clone__, __compare__, __hash__

#define OBIN_BEHAVIOR_BASE_NULL 0, 0, 0, 0, 0
#define OBIN_BEHAVIOR_COLLECTION(__iterator__,__length__,__getitem__,__setitem__,__hasitem__,__delitem__)  __iterator__, __length__, __getitem__, __setitem__, __hasitem__, __delitem__

#define OBIN_BEHAVIOR_COLLECTION_NULL 0, 0, 0, 0, 0, 0
#define OBIN_BEHAVIOR_GENERATOR(__next__)  __next__

#define OBIN_BEHAVIOR_GENERATOR_NULL 0
#define OBIN_BEHAVIOR_NUMBER_CAST(__tointeger__,__tofloat__,__topositive__,__tonegative__)  __tointeger__, __tofloat__, __topositive__, __tonegative__

#define OBIN_BEHAVIOR_NUMBER_CAST_NULL 0, 0, 0, 0
#define OBIN_BEHAVIOR_NUMBER_OPERATIONS(__abs__,__invert__,__add__,__subtract__,__divide__,__multiply__,__pow__,__leftshift__,__rightshift__,__mod__,__and__,__or__,__xor__)  __abs__, __invert__, __add__, __subtract__, __divide__, __multiply__, __pow__, __leftshift__, __rightshift__, __mod__, __and__, __or__, __xor__

#define OBIN_BEHAVIOR_NUMBER_OPERATIONS_NULL 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

#define OBIN_BEHAVIOR_DECLARE(structname) static ObinBehavior structname;

#define OBIN_BEHAVIOR_DEFINE(structname, name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER_CAST, NUMBER_OPERATIONS)  \
static ObinBehavior structname = { \
    name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER_CAST, NUMBER_OPERATIONS  \
};
#endif /* OBEHAVIOR_H_ */
