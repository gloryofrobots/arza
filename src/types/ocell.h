#ifndef OCELL_H_
#define OCELL_H_

#include "oany.h"

static ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell) {
	ObinAny result;
	obin_assert(obin_type_is_cell(type));

	result = obin_any_new();

	obin_any_init_cell(result, type, cell);

	return result;
}
ObinAny obin_cell_destroy(ObinAny cell);

#endif /* OCELL_H_ */
