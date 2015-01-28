#ifndef OBIN_OBUILTIN_H_
#define OBIN_OBUILTIN_H_
#include <types/oany.h>

/**************************** BUILTINS *******************************************/
/*TYPE TRAIT*/
ObinTypeTrait* obin_type_trait(ObinState * state, ObinAny any);
#define obin_tt_call(method, state, any) (obin_any_cell(any)->type_trait->method(state, any))
#define obin_tt_call_1(method, state, any, arg) (obin_any_cell(any)->type_trait->method(state, any, arg))
#define obin_tt_has(type_trait, method) (type_trait->method) == NULL)


ObinAny obin_hash(ObinState * state, ObinAny any);

ObinAny obin_equal(ObinState * state, ObinAny any);

/*@return list of results from function applied to iterable */
ObinAny obin_map(ObinState * state, obin_function function, ObinAny iterable);

/*Construct a list from those elements of iterable for which function returns True.*/
ObinAny obin_filter(ObinState * state, obin_function function, ObinAny iterable);

/*Apply function of two arguments cumulatively to the items of iterable,
 *  from left to right, so as to reduce the iterable to a single value..*/
ObinAny obin_reduce(ObinState * state, obin_function_2 function, ObinAny iterable);

/*Returns true if object is iterable*/
ObinAny obin_any_is_iterable(ObinState * state, ObinAny iterable);

ObinAny obin_destroy(ObinState * state, ObinAny dead);

/*Returns iterator if can, else raise InvalidArgumentError*/
ObinAny obin_iterator(ObinState * state, ObinAny iterable);
/*Returns next value from iterator, Nothing if end*/
ObinAny obin_next(ObinState * state, ObinAny iterator);

#endif
