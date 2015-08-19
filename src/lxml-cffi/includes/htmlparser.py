import cffi
from . import xmlparser

ffi = cffi.FFI()
ffi.include(xmlparser.ffi)
ffi.cdef("""
    /*
     * Most of the back-end structures from XML and HTML are shared.
     */
    typedef xmlParserCtxt htmlParserCtxt;
    typedef xmlParserCtxtPtr htmlParserCtxtPtr;
    typedef xmlSAXHandlerPtr htmlSAXHandlerPtr;
    typedef xmlDocPtr htmlDocPtr;

    #define HTML_PARSE_NOERROR ...   // suppress error reports
    #define HTML_PARSE_NOWARNING ... // suppress warning reports
    #define HTML_PARSE_PEDANTIC ...  // pedantic error reporting
    #define HTML_PARSE_NOBLANKS ...  // remove blank nodes
    #define HTML_PARSE_NONET ...     // Forbid network access
    // libxml2 2.6.21+ only:
    #define HTML_PARSE_RECOVER ...   // Relaxed parsing
    #define HTML_PARSE_COMPACT ...   // compact small text nodes

    xmlSAXHandlerV1 htmlDefaultSAXHandler;

    htmlParserCtxtPtr 	htmlCreateMemoryParserCtxt(const char *buffer,
						   int size);
    void 	htmlCtxtReset		(htmlParserCtxtPtr ctxt);
    int 	htmlCtxtUseOptions	(htmlParserCtxtPtr ctxt,
					 int options);
    htmlDocPtr 	htmlCtxtReadFile		(xmlParserCtxtPtr ctxt,
					 const char *filename,
					 const char *encoding,
					 int options);
    htmlDocPtr 	htmlCtxtReadMemory	(xmlParserCtxtPtr ctxt,
					 const char *buffer,
					 int size,
					 const char *URL,
					 const char *encoding,
					 int options);
    htmlDocPtr 	htmlCtxtReadIO		(xmlParserCtxtPtr ctxt,
					 xmlInputReadCallback ioread,
					 xmlInputCloseCallback ioclose,
					 void *ioctx,
					 const char *URL,
					 const char *encoding,
					 int options);
    htmlDocPtr 	htmlNewDoc		(const xmlChar *URI,
					 const xmlChar *ExternalID);


    htmlParserCtxtPtr 	htmlCreatePushParserCtxt(htmlSAXHandlerPtr sax,
						 void *user_data,
						 const char *chunk,
						 int size,
						 const char *filename,
						 xmlCharEncoding enc);
    int 		htmlParseChunk		(htmlParserCtxtPtr ctxt,
						 const char *chunk,
						 int size,
						 int terminate);

""")

libxml = ffi.verify("""
    #include "libxml/relaxng.h"
    #include "libxml/HTMLparser.h"
    #include "libxml/HTMLtree.h"
""",
include_dirs=['/usr/include/libxml2'],
libraries=['xml2'])
for name in dir(libxml):
    if name.startswith(('html', 'HTML_PARSE')):
        globals()[name] = getattr(libxml, name)

htmlDefaultSAXHandler = libxml.htmlDefaultSAXHandler
