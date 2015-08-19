import cffi
from . import tree

ffi = cffi.FFI()
ffi.include(tree.ffi)
ffi.cdef("""
    typedef struct _xmlNodeSet xmlNodeSet;
    typedef xmlNodeSet *xmlNodeSetPtr;

    int xmlC14NDocSaveTo	(xmlDocPtr doc,
					 xmlNodeSetPtr nodes,
					 int mode, /* a xmlC14NMode */
					 xmlChar **inclusive_ns_prefixes,
					 int with_comments,
					 xmlOutputBufferPtr buf);
    int 	xmlC14NDocSave		(xmlDocPtr doc,
					 xmlNodeSetPtr nodes,
					 int mode, /* a xmlC14NMode */
					 xmlChar **inclusive_ns_prefixes,
					 int with_comments,
					 const char* filename,
					 int compression);

    int 	xmlC14NDocDumpMemory	(xmlDocPtr doc,
					 xmlNodeSetPtr nodes,
					 int mode, /* a xmlC14NMode */
					 xmlChar **inclusive_ns_prefixes,
					 int with_comments,
					 xmlChar **doc_txt_ptr);
""")

libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/parser.h"
    #include "libxml/c14n.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])

for name in dir(libxml):
    if name.startswith('xml'):
        globals()[name] = getattr(libxml, name)

