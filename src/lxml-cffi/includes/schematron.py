import cffi
from . import tree, xmlerror

ffi = cffi.FFI()
ffi.include(xmlerror.ffi)
ffi.include(tree.ffi)
ffi.cdef("""
    typedef struct _xmlSchematron xmlSchematron;
    typedef xmlSchematron *xmlSchematronPtr;

    typedef struct _xmlSchematronParserCtxt xmlSchematronParserCtxt;
    typedef xmlSchematronParserCtxt *xmlSchematronParserCtxtPtr;

    typedef struct _xmlSchematronValidCtxt xmlSchematronValidCtxt;
    typedef xmlSchematronValidCtxt *xmlSchematronValidCtxtPtr;

    typedef enum {
        XML_SCHEMATRON_OUT_QUIET = 1,   /* quiet no report */
        XML_SCHEMATRON_OUT_TEXT = 2,	/* build a textual report */
        XML_SCHEMATRON_OUT_XML = 4,	/* output SVRL */
        XML_SCHEMATRON_OUT_ERROR = 8,  /* output via xmlStructuredErrorFunc */
        XML_SCHEMATRON_OUT_FILE = 256,	/* output to a file descriptor */
        XML_SCHEMATRON_OUT_BUFFER = 512,	/* output to a buffer */
        XML_SCHEMATRON_OUT_IO = 1024	/* output to I/O mechanism */
    } xmlSchematronValidOptions;

    xmlSchematronParserCtxtPtr xmlSchematronNewDocParserCtxt(xmlDocPtr doc);
    void    xmlSchematronFreeParserCtxt	(xmlSchematronParserCtxtPtr ctxt);

    xmlSchematronPtr xmlSchematronParse		(xmlSchematronParserCtxtPtr ctxt);
    void    xmlSchematronFree		(xmlSchematronPtr schema);

    xmlSchematronValidCtxtPtr xmlSchematronNewValidCtxt	(xmlSchematronPtr schema,
	    				 int options);
    void    xmlSchematronFreeValidCtxt	(xmlSchematronValidCtxtPtr ctxt);
    int     xmlSchematronValidateDoc	(xmlSchematronValidCtxtPtr ctxt,
					 xmlDocPtr instance);

    void    xmlSchematronSetValidStructuredErrors(
	                                  xmlSchematronValidCtxtPtr ctxt,
					  xmlStructuredErrorFunc serror,
					  void *ctx);

""")

libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/schematron.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])

def init():
    for name in dir(libxml):
        if name.startswith(('xml', 'XML')):
            globals()[name] = getattr(libxml, name)

init()
