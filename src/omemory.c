#include <cstdlib>
#include <cstring>
#include <assert.h>
#include "omemory.h"

obin_pointer obin_malloc(obin_mem_t size) {
	obin_pointer new_pointer;

	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_MALLOC(size);
	//run gc here
	assert(new_pointer!=0);

	return new_pointer;
}

obin_pointer obin_malloc_and_fill(obin_mem_t size) {
	obin_pointer new_pointer;

	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_MALLOC(size);
	assert(new_pointer!=0);
	memset(new_pointer,'\0', size);
	return new_pointer;
}

obin_pointer obin_realloc(obin_pointer ptr, obin_mem_t size) {
	obin_pointer new_pointer;
	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_REALLOC(ptr, size);
	assert(new_pointer!=0);
	return new_pointer;
}

obin_pointer obin_memory_duplicate(obin_pointer ptr, obin_mem_t elements, obin_mem_t element_size ){
	obin_pointer new_pointer;
	obin_mem_t size;

	size = element_size * elements;

	new_pointer = obin_malloc(size);
	memcpy(new_pointer, ptr, size);

	return new_pointer;
}
