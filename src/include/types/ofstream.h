#ifndef OSTREAM_H_
#define OSTREAM_H_

#include "obuiltin.h"

#define OBIN_FSTREAM_MODE_READ "r"
#define OBIN_FSTREAM_MODE_READ_UPDATE "r+"
#define OBIN_FSTREAM_MODE_APPEND "a"
#define OBIN_FSTREAM_MODE_APPEND_UPDATE "a+"
#define OBIN_FSTREAM_MODE_WRITE "w"
#define OBIN_FSTREAM_MODE_WRITE_UPDATE "w+"

OAny obin_fstream_from_file(OState* state, obin_file file,
		obin_bool is_disposable);
OAny obin_fstream_from_path(OState* state, OAny path, obin_string mode);
OAny obin_fstream_write_va(OState* state, OAny self, obin_string format, ...);
OAny obin_fstream_write(OState* state, OAny self, OAny any);
OAny obin_fstream_close(OState* state, OAny self);
OAny obin_fstream_is_open(OState* state, OAny self);

#endif /* OSTREAM_H_ */
