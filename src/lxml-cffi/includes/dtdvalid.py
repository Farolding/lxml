import cffi
from . import tree

ffi = cffi.FFI()
ffi.include(tree.ffi)

ffi.cdef("""
    typedef struct _xmlValidCtxt xmlValidCtxt;
    typedef xmlValidCtxt *xmlValidCtxtPtr;
    typedef void (*xmlValidityErrorFunc)(void * ctx, const char * msg, ...);
    typedef void (*xmlValidityWarningFunc)(void * ctx, const char * msg, ...);

    struct _xmlValidCtxt {
        void *userData;
        xmlValidityErrorFunc error;
        xmlValidityWarningFunc warning;
        ...;
    };

    xmlValidCtxtPtr xmlNewValidCtxt(void);
    void xmlFreeValidCtxt(xmlValidCtxtPtr);
    int 	xmlValidateDtd		(xmlValidCtxtPtr ctxt,
					 xmlDocPtr doc,
					 xmlDtdPtr dtd);
    xmlElementPtr	xmlGetDtdElementDesc	(xmlDtdPtr dtd, 
					 const xmlChar * name);
""")

libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/parser.h"
    #include "libxml/valid.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])

for name in dir(libxml):
    if name.startswith('xml'):
        globals()[name] = getattr(libxml, name)

