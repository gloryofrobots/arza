#ifndef OSTREAM_H_
#define OSTREAM_H_

#include "obuiltin.h"

#define OBIN_FSTREAM_MODE_READ "r"
#define OBIN_FSTREAM_MODE_READ_UPDATE "r+"
#define OBIN_FSTREAM_MODE_APPEND "a"
#define OBIN_FSTREAM_MODE_APPEND_UPDATE "a+"
#define OBIN_FSTREAM_MODE_WRITE "w"
#define OBIN_FSTREAM_MODE_WRITE_UPDATE "w+"

ObinAny obin_fstream_from_file(ObinState* state, obin_file file,
		obin_bool is_disposable);
ObinAny obin_fstream_from_path(ObinState* state, ObinAny path, obin_string mode);
ObinAny obin_fstream_write_va(ObinState* state, ObinAny self, obin_string format, ...);
ObinAny obin_fstream_write(ObinState* state, ObinAny self, ObinAny any);
ObinAny obin_fstream_close(ObinState* state, ObinAny self);
ObinAny obin_fstream_is_open(ObinState* state, ObinAny self);

#endif /* OSTREAM_H_ */
