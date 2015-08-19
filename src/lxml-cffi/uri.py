import cffi

ffi = cffi.FFI()
ffi.cdef("""
    typedef struct _xmlURI xmlURI;
    typedef xmlURI *xmlURIPtr;
    xmlURIPtr 	xmlParseURI		(const char *str);
    void 	xmlFreeURI		(xmlURIPtr uri);

""")

libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/uri.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])

for name in dir(libxml):
    if name.startswith('xml'):
        globals()[name] = getattr(libxml, name)


