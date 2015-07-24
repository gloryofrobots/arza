#ifndef OSTREAM_H_
#define OSTREAM_H_

#include "obuiltin.h"

#define OBIN_FSTREAM_MODE_READ "r"
#define OBIN_FSTREAM_MODE_READ_UPDATE "r+"
#define OBIN_FSTREAM_MODE_APPEND "a"
#define OBIN_FSTREAM_MODE_APPEND_UPDATE "a+"
#define OBIN_FSTREAM_MODE_WRITE "w"
#define OBIN_FSTREAM_MODE_WRITE_UPDATE "w+"

OAny obin_fstream_from_file(ObinState* state, obin_file file,
		obin_bool is_disposable);
OAny obin_fstream_from_path(ObinState* state, OAny path, obin_string mode);
OAny obin_fstream_write_va(ObinState* state, OAny self, obin_string format, ...);
OAny obin_fstream_write(ObinState* state, OAny self, OAny any);
OAny obin_fstream_close(ObinState* state, OAny self);
OAny obin_fstream_is_open(ObinState* state, OAny self);

#endif /* OSTREAM_H_ */
