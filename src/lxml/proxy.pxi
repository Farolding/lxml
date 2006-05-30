# Proxy functions

# Proxies represent elements, their reference is stored in the C
# structure of the respective node to avoid multiple instantiation of
# the Python class

cdef struct _ProxyRef

cdef struct _ProxyRef:
    python.PyObject* proxy
    LXML_PROXY_TYPE type
    _ProxyRef* next
        
ctypedef _ProxyRef ProxyRef

cdef _NodeBase getProxy(xmlNode* c_node, int proxy_type):
    """Get a proxy for a given node and node type.
    """
    cdef ProxyRef* ref
    #print "getProxy for:", <int>c_node
    if c_node is NULL:
        return None
    ref = <ProxyRef*>c_node._private
    while ref is not NULL:
        if ref.type == proxy_type:
            return <_NodeBase>ref.proxy
        ref = ref.next
    return None

cdef int hasProxy(xmlNode* c_node):
    return c_node._private is not NULL
    
cdef void registerProxy(_NodeBase proxy, int proxy_type):
    """Register a proxy and type for the node it's proxying for.
    """
    cdef xmlNode* c_node
    cdef ProxyRef* ref
    # cannot register for NULL
    c_node = proxy._c_node
    if c_node is NULL:
        return
    # XXX should we check whether we ran into proxy_type before?
    #print "registering for:", <int>proxy._c_node
    ref = <ProxyRef*>python.PyMem_Malloc(sizeof(ProxyRef))
    ref.proxy = <python.PyObject*>proxy
    ref.type = proxy_type
    ref.next = <ProxyRef*>c_node._private
    c_node._private = ref # prepend

cdef void unregisterProxy(_NodeBase proxy):
    """Unregister a proxy for the node it's proxying for.
    """
    cdef python.PyObject* proxy_ref
    cdef ProxyRef* ref
    cdef ProxyRef* prev_ref
    cdef xmlNode* c_node
    proxy_ref = <python.PyObject*>proxy
    c_node = proxy._c_node
    ref = <ProxyRef*>c_node._private
    if ref.proxy == proxy_ref:
        c_node._private = <void*>ref.next
        python.PyMem_Free(ref)
        return
    prev_ref = ref
    #print "First registered is:", ref.type
    ref = ref.next
    while ref is not NULL:
        #print "Registered is:", ref.type
        if ref.proxy == proxy_ref:
            prev_ref.next = ref.next
            python.PyMem_Free(ref)
            return
        prev_ref = ref
        ref = ref.next
    #print "Proxy:", proxy, "Proxy type:", proxy_type
    assert 0, "Tried to unregister unknown proxy"

################################################################################
# temporarily make a node the root node of its document

cdef xmlDoc* _fakeRootDoc(xmlDoc* c_base_doc, xmlNode* c_node):
    # build a temporary document that has the given node as root node
    # note that copy and original must not be modified during its lifetime!!
    # always call _destroyFakeDoc() after use!
    cdef xmlNode* c_child
    cdef xmlNode* c_root
    cdef xmlDoc*  c_doc
    c_root = tree.xmlDocGetRootElement(c_base_doc)
    if c_root is c_node:
        # already the root node
        return c_base_doc

    c_doc  = _copyDoc(c_base_doc, 0)               # non recursive!
    c_root = tree.xmlDocCopyNode(c_node, c_doc, 2) # non recursive!
    tree.xmlDocSetRootElement(c_doc, c_root)

    c_root.children = c_node.children
    c_root.last = c_node.last
    c_root.next = c_root.prev = c_root.parent = NULL

    # store original node
    c_doc._private = c_node

    # divert parent pointers of children
    c_child = c_root.children
    while c_child is not NULL:
        c_child.parent = c_root
        c_child = c_child.next

    c_doc.children = c_root
    return c_doc

cdef void _destroyFakeDoc(xmlDoc* c_base_doc, xmlDoc* c_doc):
    # delete a temporary document
    cdef xmlNode* c_child
    cdef xmlNode* c_parent
    cdef xmlNode* c_root
    if c_doc != c_base_doc:
        c_root = tree.xmlDocGetRootElement(c_doc)

        # restore parent pointers of children
        c_parent = <xmlNode*>c_doc._private
        c_child = c_root.children
        while c_child is not NULL:
            c_child.parent = c_parent
            c_child = c_child.next

        # prevent recursive removal of children
        c_root.children = c_root.last = NULL
        tree.xmlFreeDoc(c_doc)

################################################################################
# support for freeing tree elements when proxy objects are destroyed

cdef void attemptDeallocation(xmlNode* c_node):
    """Attempt deallocation of c_node (or higher up in tree).
    """
    cdef xmlNode* c_top
    # could be we actually aren't referring to the tree at all
    if c_node is NULL:
        #print "not freeing, node is NULL"
        return
    c_top = getDeallocationTop(c_node)
    if c_top is not NULL:
        #print "freeing:", c_top.name
        tree.xmlFreeNode(c_top)

cdef xmlNode* getDeallocationTop(xmlNode* c_node):
    """Return the top of the tree that can be deallocated, or NULL.
    """
    cdef xmlNode* c_current
    cdef xmlNode* c_top
    #print "trying to do deallocating:", c_node.type
    if c_node._private is not NULL:
        #print "Not freeing: proxies still exist"
        return NULL
    c_current = c_node.parent
    c_top = c_node
    while c_current is not NULL:
        #print "checking:", c_current.type
        if c_current.type == tree.XML_DOCUMENT_NODE or \
               c_current.type == tree.XML_HTML_DOCUMENT_NODE:
            #print "not freeing: still in doc"
            return NULL
        # if we're still attached to the document, don't deallocate
        if c_current._private is not NULL:
            #print "Not freeing: proxies still exist"
            return NULL
        c_top = c_current
        c_current = c_current.parent
    # see whether we have children to deallocate
    if canDeallocateChildren(c_top):
        return c_top
    else:
        return NULL

cdef int canDeallocateChildNodes(xmlNode* c_node):
    cdef xmlNode* c_current
    c_current = c_node.children
    while c_current is not NULL:
        if c_current._private is not NULL:
            return 0
        if not canDeallocateChildren(c_current):
            return 0 
        c_current = c_current.next
    return 1

cdef int canDeallocateAttributes(xmlNode* c_node):
    cdef xmlAttr* c_current
    c_current = c_node.properties
    while c_current is not NULL:
        if c_current._private is not NULL:
            return 0
        # only check child nodes, don't try checking properties as
        # attribute has none
        if not canDeallocateChildNodes(<xmlNode*>c_current):
            return 0
        c_current = c_current.next
    # apparently we can deallocate all subnodes
    return 1

cdef int canDeallocateChildren(xmlNode* c_node):
    # the current implementation is inefficient as it does a
    # tree traversal to find out whether there are any node proxies
    # we could improve this by a smarter datastructure
    # check children
    if not canDeallocateChildNodes(c_node):
        return 0
    # check any attributes
    if (c_node.type == tree.XML_ELEMENT_NODE and
        not canDeallocateAttributes(c_node)):
        return 0
    # apparently we can deallocate all subnodes
    return 1

