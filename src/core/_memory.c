#include <obin.h>

#define _end_heap(memory)  (memory->object_space + memory->OBJECT_SPACE_SIZE)
#define _heap(memory)  (memory->object_space)

#define ObinMem_Padding(N) ((sizeof(obin_pointer) - ((N) % sizeof(obin_pointer))) % sizeof(obin_pointer))

#define ObinMem_Malloc(n) ((obin_mem_t)(n) > OBIN_MEM_MAX? NULL \
				: malloc((n) ? (n) : 1))

#define ObinMem_Realloc(p, n)	((obin_mem_t)(n) > (obin_mem_t)OBIN_MEM_MAX  ? NULL \
				: realloc((p), (n) ? (n) : 1))

#define ObinMem_Free free

#define OBIN_B_TO_KB(B) (B/1024)
#define OBIN_B_TO_MB(B) ((double)B/(1024.0*1024.0))
#define OBIN_KB_TO_B(KB) (KB * 1024)
#define OBIN_MB_TO_B(MB) (MB * 1024 * 1024)

#define CATCH_STATE_MEMORY(state) \
	ObinMemory* M = state->memory; \
	if(!M) { obin_panic("ObinState memory is NULL!"); }

/*FORWARDS */
void gc_merge_free_spaces(ObinState*);
void init_collect_stat(ObinState*);
void collect_stat(ObinState*);
void reset_alloc_stat(ObinState*);

/* LOG */
void _log(ObinState* state, obin_string format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stdout, format, myargs);
	va_end(myargs);
}

void _panic(ObinState* state, obin_string format, ...) {
	va_list myargs;
	va_start(myargs, format);
	obin_vfprintf(stderr, format, myargs);
	va_end(myargs);
	obin_abort();
}

/* MEMORY PRIMITIVES */
obin_pointer obin_malloc(ObinState * state, obin_mem_t size) {
	obin_pointer new_pointer;

	if (!size) {
		/*TODO MAYBE SIGNAL HERE */
		return NULL;
	}

	new_pointer = ObinMem_Malloc(size);
/*	run gc here*/
	if(!new_pointer) {
    	_panic(state, "Failed to allocate the initial %d bytes for the GC. Panic.\n",
                (int) size);

    	return NULL;
	}

	memset(new_pointer, 0, size);
	return new_pointer;
}

obin_pointer obin_realloc(ObinState * state, obin_pointer ptr, obin_mem_t size) {
	obin_pointer new_pointer;
	if (!size) {
		return NULL;
	}

	new_pointer = ObinMem_Realloc(ptr, size);
	assert(new_pointer != 0);
	return new_pointer;
}

obin_pointer obin_memory_duplicate(ObinState * state, obin_pointer ptr,
		obin_mem_t elements, obin_mem_t element_size) {
	obin_pointer new_pointer;
	obin_mem_t size;

	size = element_size * elements;

	new_pointer = obin_malloc(state, size);
	memcpy(new_pointer, ptr, size);

	return new_pointer;
}


/* REF COUNT */
ObinAny obin_hold(ObinState* state, ObinAny any) {
	obin_any_cell(any)->memory.lives++;
	obin_any_cell(any)->memory.rc++;

	return any;
}

ObinAny obin_release(ObinState* state, ObinAny any) {
	obin_any_cell(any)->memory.deads++;
	obin_any_cell(any)->memory.rc--;

	return any;
}
/* GC and Allocator */

void _memory_create(ObinState* state, obin_mem_t heap_size) {
	ObinMemory* M;
	state->memory = (ObinMemory*) obin_malloc(state, sizeof(ObinMemory));
	M = state->memory;

	if(!M) {
		obin_panic("Not enough memory to allocate State");
	}

    M->OBJECT_SPACE_SIZE = heap_size;

    /* Buffersize is adjusted to the size of the heap (10%) */
    M->BUFFERSIZE_FOR_UNINTERRUPTABLE = (int) (M->OBJECT_SPACE_SIZE * 0.1);

    /* allocation of the heap */
    M->object_space = ObinMem_Malloc(M->OBJECT_SPACE_SIZE);
    if (!M->object_space) {
    	_panic(state, "Failed to allocate the initial %d bytes for the GC. Panic.\n",
                (int) M->OBJECT_SPACE_SIZE);
    }

    obin_memset(M->object_space, 0, M->OBJECT_SPACE_SIZE);
    M->size_of_free_heap = M->OBJECT_SPACE_SIZE;

    /* initialize free_list by creating the first */
    /* entry, which contains the whole object_space */
    M->first_free_entry = (free_list_entry*) M->object_space;
    M->first_free_entry->size = M->OBJECT_SPACE_SIZE;
    M->first_free_entry->next = NULL;

    /* initialise statistical counters */
    M->num_collections = 0;

    /* these two need to be initially set here, as they have to be preserved */
    /* across collections and cannot be reset in init_collect_stat() */
    M->num_alloc = 0;
    M->spc_alloc = 0;
}

void _memory_destroy(ObinState* state) {
	ObinMem_Free(state->memory->object_space);
	ObinMem_Free(state->memory);
	state->memory = 0;
}

ObinState* obin_state_new() {
	ObinState* state;
	obin_mem_t size;
    size = sizeof(ObinState);
	state = ObinMem_Malloc(size);
	if(!state) {
    	obin_panic("Failed to allocate ObinState");
    	return NULL;
	}

	memset(state, 0, size);
	_memory_create(state, OBIN_DEFAULT_HEAP_SIZE);
	return state;
}

void obin_state_destroy(ObinState* state) {
	ObinMem_Free(state->memory->object_space);
    ObinMem_Free(state->memory);
	ObinMem_Free(state);
}

/**
 *  check whether the object is inside the managed heap
 *  if it isn't, there is no VMObject to mark, otherwise
 *  check whether the object is already marked.
 *  if the self is an unmarked object inside the heap, then
 *  it is told to 'mark_references', recursively using this
 *  function for all its references.
 */
void gc_mark_object(ObinState* state, ObinAny object) {
	ObinCell* cell = obin_any_cell(object);
	CATCH_STATE_MEMORY(state);

    if (   ((void*) cell < (void*)  _heap(M))
        || ((void*) cell > (void*) _end_heap(M)))
    {
		_log(state, "GC encountered object not belong to allocator heap");
		return;
    }

	if (cell->memory.mark == 1) {
		return;
	}

	cell->memory.mark = 1;
	M->num_live++;
	M->spc_live += cell->memory.size;

	if(!cell->native_traits) {
		_log(state, "GC encountered object without traits");
		return;
	}

	if(!cell->native_traits->base) {
		_log(state, "GC encountered object without traits");
		return;
	}

	if(!cell->native_traits->base->__foreach_internal_objects__) {
		return;
	}

	cell->native_traits->base->__foreach_internal_objects__(state, object, &gc_mark_object);
}

void gc_mark_reachable_objects(ObinState * state) {
	ObinAny globals = state->globals;
	gc_mark_object(state, globals);

	/*     Get the current frame and mark it.
    Since marking is done recursively, this automatically
	marks the whole stack
    pVMFrame current_frame = (pVMFrame) Interpreter_get_frame();
    if (current_frame != NULL) {
        gc_mark_object(current_frame);
    }*/
}


/**
 * For debugging - the layout of the heap is shown.
 * This function uses
 * - '[size]' for free space,
 * - '-xx-' for marked objects, and
 * - '-size-' for unmarked objects.
 * The output is also aligned to improve readability.
 */
void gc_show_memory(ObinState* state) {
    ObinCell* pointer;
    free_list_entry* current_entry;
    int object_size = 0;
    int object_aligner = 0;
    int line_count = 2;
    ObinCell* object;
	CATCH_STATE_MEMORY(state);

    pointer = M->object_space;
    current_entry = M->first_free_entry;

    _log(state, "\n########\n# SHOW #\n########\n");

    do {
        while (((void*)pointer > (void*)current_entry->next) && (current_entry->next != NULL)) {
            current_entry = current_entry->next;
        }

        if ((   (void*)current_entry->next == (void*)pointer)
            || ((void*)current_entry == (void*)pointer))
        {
            if ((void*)current_entry == (void*)pointer) {
                object_size = current_entry->size;
            } else {
                free_list_entry* next = current_entry->next;
                object_size = next->size;
            }
            _log(state, "[%d]",object_size);
        } else {
            object = pointer;

            /*here we need recursive function maybe*/
            object_size = object->memory.size;

            /* is this object marked or not? */
            if (object->memory.mark == 1) {
            	_log(state, "-xx-");
            }

            _log(state, "-%d %s %p-", object_size, object->native_traits->name, object);
        }
        /* aligns the output by inserting a line break after 36 objects */
        object_aligner++;
        if (object_aligner == 36) {
            _log(state, "\n%d ", line_count++);
            object_aligner = 0;
        }
        _log(state, "\n");
        pointer = (void*)((int)pointer + object_size);
    } while ((void*)pointer < (void*)(_end_heap(M)));
}

void obin_gc_collect(ObinState* state) {
	obin_pointer pointer;
	ObinCell* object;
	free_list_entry* current_entry, *new_entry;
    int object_size = 0;
	CATCH_STATE_MEMORY(state);

    M->num_collections++;
    init_collect_stat(state);

    gc_mark_reachable_objects(state);
	_log(state, "-- pre-collection heap dump --\n");
	gc_show_memory(state);

    pointer = M->object_space;
    current_entry = M->first_free_entry;
    do {
        /* we need to find the last free entry before the pointer */
        /* whose 'next' lies behind or is the pointer */
        while (((void*)pointer > (void*)current_entry->next) && (current_entry->next != NULL)) {
            current_entry = current_entry->next;
        }

        if (((void*)current_entry->next == (void*)pointer) || ((void*)current_entry == (void*)pointer)) {
            /* in case the pointer is the part of the free_list: */
            if ((void*)current_entry == (void*)pointer) {
                object_size = current_entry->size;
            } else {
                free_list_entry* next = current_entry->next;
                object_size = next->size;
            }
            /*fprintf(stderr,"[%d]",object_size); */
            /* nothing else to be done here */
        } else {
            /* in this case the pointer is a VMObject */
            object = (ObinCell*) pointer;
            object_size = object->memory.size;
            /* is this object marked or not? */
            if (object->memory.mark == 1) {
                /* remove the marking */
                object->memory.mark = 0;
            } else {
                M->num_freed++;
                M->spc_freed += object_size;
                /* add new entry containing this object to the free_list */
                obin_destroy(state, object);
                memset(object, 0, object_size);
                new_entry = ((free_list_entry*) pointer);
                new_entry->size = object_size;

                /* if the new entry lies before the first entry, */
                /* adjust the pointer to the first one */
                if (new_entry < M->first_free_entry) {
                    new_entry->next = M->first_free_entry;
                    M->first_free_entry = new_entry;
                    current_entry = new_entry;
                } else {
                    /* insert the newly created entry right after the current entry */
                    new_entry->next = current_entry->next;
                    current_entry->next = new_entry;
                }
            }
        }
        /* set the pointer to the next object in the heap */
        pointer = (void*)((int)pointer + object_size);

    } while ((void*)pointer < (void*)(_end_heap(M)));

    /* combine free_entries, which are next to each other */
    gc_merge_free_spaces(state);

    collect_stat(state);
	_log(state, "-- post-collection heap dump --\n");
	gc_show_memory(state);
    reset_alloc_stat(state);
}

void* _allocate_cell(ObinState* state, obin_mem_t size) {
    void* result = NULL;
	free_list_entry* entry, *before_entry, *old_next, *replace_entry;
	int old_entry_size;
	CATCH_STATE_MEMORY(state);

    if(size == 0) {
    	return NULL;
    }

    if(size < sizeof(free_list_entry)) {
    	_panic(state, "Can`t allocate so small chunk in allocator %d", size);
    	return NULL;
    }

    /* start garbage collection if the free heap has less */
    /* than BUFFERSIZE_FOR_UNINTERRUPTABLE Bytes and this */
    /* allocation is interruptable */
    if (M->size_of_free_heap <= M->BUFFERSIZE_FOR_UNINTERRUPTABLE) {
    	obin_gc_collect(state);
    }

    /* initialize variables to search through the free_list */
    entry = M->first_free_entry;
    before_entry = NULL;

    /* don't look for the perfect match, but for the first-fit */
    while (! ((entry->size == size)
               || (entry->next == NULL)
               || (entry->size >= (size + sizeof(free_list_entry))))) {
        before_entry = entry;
        entry = entry->next;
    }

    /* did we find a perfect fit? */
    /* if so, we simply remove this entry from the list */
    if (entry->size == size) {
        if (entry == M->first_free_entry) {
            /* first one fitted - adjust the 'first-entry' pointer */
            M->first_free_entry = entry->next;
        } else {
            /* simply remove the reference to the found entry */
            before_entry->next = entry->next;
        } /* entry fitted */
        result = entry;

    } else {
        /* did we find an entry big enough for the request and a new */
        /* free_entry? */
        if (entry->size >= (size + sizeof(free_list_entry))) {
            /* save data from found entry */
            old_entry_size = entry->size;
            old_next = entry->next;

            result = entry;
            /* create new entry and assign data */
            replace_entry =  (free_list_entry*) ((int)entry + size);

            replace_entry->size = old_entry_size - size;
            replace_entry->next = old_next;
            if (entry == M->first_free_entry) {
                M->first_free_entry = replace_entry;
            } else {
                before_entry->next = replace_entry;
            }
        }  else {
            /* no space was left */
            /* running the GC here will most certainly result in data loss! */
            _log(state ,"Not enough heap! Data loss is possible\n");
            _log(state, "FREE-Size: %d, uninterruptable_counter: %d\n",
                M->size_of_free_heap, M->uninterruptable_counter);

            obin_gc_collect(state);
            /*fulfill initial request */
            result = _allocate_cell(state, size);
        }
    }

    if(!result) {
        _panic(state, "Failed to allocate %d bytes. Panic.\n", (int)size);
    }

    memset(result, 0, size);
    /* update the available size */
    M->size_of_free_heap -= size;
    return result;
}

void* obin_allocate_cell(ObinState* state, obin_mem_t size) {
	obin_mem_t aligned_size = size + ObinMem_Padding(size);
    ObinCell* object = (ObinCell*)_allocate_cell(state, aligned_size);

    if(!object) {
    	return NULL;
    }

    object->memory.size = aligned_size;
    state->memory->num_alloc++;
    state->memory->spc_alloc += aligned_size;
    return object;
}


/**
 * this function must not do anything, since the heap management
 * is done inside gc_collect.
 * However, it is called upon by all VMObjects.
 */
void obin_free(ObinState* state, obin_pointer ptr) {
#ifdef ODEBUG
	CATCH_STATE_MEMORY(state);
    /* check if called for an object inside the object_space */
    if ((   ptr >= (void*)  M->object_space)
        && (ptr < (void*) (M->object_space + M->OBJECT_SPACE_SIZE)))
    {
    	obin_panic("free called for an object in allocator");
    }
#endif
    ObinMem_Free(ptr);
}

/* free entries which are next to each other are merged into one entry */
void gc_merge_free_spaces(ObinState* state) {
	ObinMemory* M = state->memory;
    free_list_entry* entry = M->first_free_entry;
    free_list_entry* entry_to_append = NULL;
    int new_size = 0;
    free_list_entry* new_next = NULL;

    M->size_of_free_heap = 0;

    while (entry->next != NULL) {
        if (((int)entry + (int)(entry->size)) == (int)(entry->next)) {
            entry_to_append = entry->next;
            new_size = entry->size + entry_to_append->size;
            new_next = entry_to_append->next;

            memset(entry_to_append, 0, entry_to_append->size);
            entry->next = new_next;
            entry->size = new_size;
        } else {
            M->size_of_free_heap += entry->size;
            entry = entry->next;
        }
    }
    if (entry->next == NULL) {
        M->size_of_free_heap += entry->size;
    } else {
    	_panic(state, "Missed last free_entry of GC\n");
    }
}
/**
 * if this counter is gt zero, an object initialization is
 * in progress. This means, that most certainlt, there are
 * objects, which are not reachable by the rootset, therefore,
 * the garbage collection would result in data loss and must
 * not be started!
 */
void gc_start_uninterruptable_allocation(ObinState* state) {
    state->memory->uninterruptable_counter++;
}

/**
 * only if the counter reaches zero, it is safe to start the
 * garbage collection.
 */
void gc_end_uninterruptable_allocation(ObinState* state) {
    state->memory->uninterruptable_counter--;
}

/*
 functions for GC statistics and debugging output
 * initialise per-collection statistics
 */
void init_collect_stat(ObinState* state) {
	CATCH_STATE_MEMORY(state);
    /* num_alloc and spc_alloc are not initialised here - they are reset after
     * the collection in reset_alloc_stat() */
    M->num_live = 0;
    M->spc_live = 0;
    M->num_freed = 0;
    M->spc_freed = 0;
}

/*
 * reset allocation statistics
 */
void reset_alloc_stat(ObinState* state) {
	CATCH_STATE_MEMORY(state);
    M->num_alloc = 0;
    M->spc_alloc = 0;
}

/*
 * Output garbage collection statistics. This function is called at the end of
 * a VM run.
 */
void gc_stat(ObinState* state) {
	CATCH_STATE_MEMORY(state);
    _log(state, "-- GC statistics --\n");
    _log(state, "* heap size %d B (%d kB, %.2f MB)\n",
        M->OBJECT_SPACE_SIZE, OBIN_B_TO_KB(M->OBJECT_SPACE_SIZE), OBIN_B_TO_MB(M->OBJECT_SPACE_SIZE));
    _log(state, "* performed %d collections\n", M->num_collections);
}

/*
 * output per-collection statistics
 */
void collect_stat(ObinState* state) {
	CATCH_STATE_MEMORY(state);
    _log(state, "\n[GC %d, %d alloc (%d kB), %d live (%d kB), %d freed "\
        "(%d kB)]\n",
        M->num_collections, M->num_alloc, OBIN_B_TO_KB(M->spc_alloc), M->num_live, OBIN_B_TO_KB(M->spc_live),
        M->num_freed, OBIN_B_TO_KB(M->spc_freed));
}
