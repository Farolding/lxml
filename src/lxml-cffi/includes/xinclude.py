import cffi
from . import tree

ffi = cffi.FFI()
ffi.include(tree.ffi)
ffi.cdef("""
    int 	xmlXIncludeProcessTreeFlags(xmlNodePtr tree,
					 int flags);
    int		xmlXIncludeProcessTreeFlagsData(xmlNodePtr tree,
					 int flags,
					 void *data);
""")
libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/xinclude.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])

def init():
    for name in dir(libxml):
        if name.startswith(('xml', 'XML')):
            globals()[name] = getattr(libxml, name)

init()
