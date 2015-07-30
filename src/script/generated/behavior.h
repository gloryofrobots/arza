
typedef struct _OBehavior {
    ostring __name__;
    /*MEMORY*/
    odestructor __destroy__;
    ofunc_each __mark__;
    /*BASE*/
    ofunc_1 __tostring__;
    ofunc_1 __tobool__;
    ofunc_1 __clone__;
    ofunc_2 __compare__;
    ofunc_2 __equal__;
    ofunc_1 __hash__;
    /*COLLECTION*/
    ofunc_1 __iterator__;
    ofunc_1 __length__;
    ofunc_2 __getitem__;
    ofunc_2 __hasitem__;
    ofunc_2 __delitem__;
    ofunc_3 __setitem__;
    /*GENERATOR*/
    ofunc_1 __next__;
    /*NUMBER*/
    ofunc_1 __tointeger__;
    ofunc_1 __tofloat__;
    ofunc_1 __tonegative__;
    ofunc_1 __invert__;
    ofunc_2 __add__;
    ofunc_2 __subtract__;
    ofunc_2 __divide__;
    ofunc_2 __multiply__;
    ofunc_2 __leftshift__;
    ofunc_2 __rightshift__;
    ofunc_2 __mod__;
    ofunc_2 __bitand__;
    ofunc_2 __bitor__;
    ofunc_2 __bitxor__;
} OBehavior;
    
#define OBEHAVIOR_MEMORY(__destroy__,__mark__)  __destroy__, __mark__ 

#define OBEHAVIOR_MEMORY_NULL 0, 0 
#define OBEHAVIOR_BASE(__tostring__,__tobool__,__clone__,__compare__,__hash__,__equal__)  __tostring__, __tobool__, __clone__, __compare__, __hash__, __equal__ 

#define OBEHAVIOR_BASE_NULL 0, 0, 0, 0, 0, 0 
#define OBEHAVIOR_COLLECTION(__iterator__,__length__,__getitem__,__hasitem__,__delitem__,__setitem__)  __iterator__, __length__, __getitem__, __hasitem__, __delitem__, __setitem__ 

#define OBEHAVIOR_COLLECTION_NULL 0, 0, 0, 0, 0, 0 
#define OBEHAVIOR_GENERATOR(__next__)  __next__ 

#define OBEHAVIOR_GENERATOR_NULL 0 
#define OBEHAVIOR_NUMBER(__tointeger__,__tofloat__,__tonegative__,__invert__,__add__,__subtract__,__divide__,__multiply__,__leftshift__,__rightshift__,__mod__,__bitand__,__bitor__,__bitxor__)  __tointeger__, __tofloat__, __tonegative__, __invert__, __add__, __subtract__, __divide__, __multiply__, __leftshift__, __rightshift__, __mod__, __bitand__, __bitor__, __bitxor__ 

#define OBEHAVIOR_NUMBER_NULL 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 

#define OBEHAVIOR_DECLARE(structname) static OBehavior structname;

#define OBEHAVIOR_DEFINE(structname, name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER)  \ 
static OBehavior structname = { \ 
    name, MEMORY, BASE, COLLECTION, GENERATOR, NUMBER  \ 
};
