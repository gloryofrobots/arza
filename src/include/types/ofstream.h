#ifndef OSTREAM_H_
#define OSTREAM_H_

#include "obuiltin.h"

#define OBIN_FSTREAM_MODE_READ "r"
#define OBIN_FSTREAM_MODE_READ_UPDATE "r+"
#define OBIN_FSTREAM_MODE_APPEND "a"
#define OBIN_FSTREAM_MODE_APPEND_UPDATE "a+"
#define OBIN_FSTREAM_MODE_WRITE "w"
#define OBIN_FSTREAM_MODE_WRITE_UPDATE "w+"

OAny OFstream_fromFile(OState* state, ofile file,
		obool is_disposable);
OAny OFstream_fromPath(OState* state, OAny path, ostring mode);
OAny OFstream_writeVA(OState* state, OAny self, ostring format, ...);
OAny OFstream_write(OState* state, OAny self, OAny any);
OAny OFstream_close(OState* state, OAny self);
OAny OFstream_isOpen(OState* state, OAny self);

#endif /* OSTREAM_H_ */
