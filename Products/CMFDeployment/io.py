"""
a new policy xml export/import system, utilizes a genericized form that allows for
just passing nested python types [json like] (lists,dictionaries, etc,)  to the exporter, and
getting the same back from the importer.

construction in turn follows from the python data structure, and is pluggable
by registering against a handler against path into the data structure.

compatibility for the new impl is in two stages, on old xml formats
we use the old parser for a release cycle, the old format is now depreceated.

for the new format, compatibility will be via a series of python transforms
applied the nested python data structure.



$Id: io.py 1658 2006-09-13 22:29:47Z hazmat $
"""

import time, types, StringIO
from xml.sax.saxutils import XMLGenerator, escape
from xml.sax.xmlreader import AttributesNSImpl
from xml.sax import make_parser, ContentHandler

import reader as policy_reader # we use content handler dispatch to preserve compatibility

_marker = object()

class struct( dict ):
    # used on import for easier value access
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            try:
                return self[unicode(key)]
            except:
                pass
            raise AttributeError( key )
        
    def __setattr__(self, key, value ):
        self[key]=value


def boolreader( value=None ):
    if isinstance( value, (str, unicode )):
        if value.lower() in ('false', 'f'):
            value = False
        elif value.lower() in ('true', 't'):
            value = True
        else:
            value = False
        return value
    if value is None:
        return False
    return bool( value )

class ImportReader( ContentHandler ):

    _types = {
        u"string" : types.StringType,
        u"int" : types.IntType,
        u"bool" : boolreader,
        u"dict" : struct, #types.DictType,
        u"list" : types.ListType
        }

    subnode_types = ( types.ListType, types.DictType, types.TupleType, struct )

    def __init__(self):
        self.buf = []
        self.root = {}
        self.current_path = ''
        self.current_type = u'string'
        self.stack = []
    
    def getData(self):
        return self.root
        
    def startElement( self, element_name, attrs ):
        d = {}
        for k, v in attrs.items():
            d[str(k)] = str(v)
        v_type = d.get('type')

        # everything in the new format should have a type code.

        self.current_path += ".%s"%element_name
        self.stack.append( v_type )

        if v_type is None:
            v_type = 'dict'

        factory = self._types[ v_type ]
        
        if factory in self.subnode_types:
            self.createData( self.current_path, v_type )

        if len(d) > 1: # has 'real' attributes
            assert d['type'] == 'dict'
            del d['type']
            path = self.current_path + ".attributes"
            self.createData( path, 'dict', d)
            
    def endElement( self, element_name ):
        assert self.current_path.endswith( element_name ), "%s %s"%( self.current_path, element_name )
        
        if self.buf and not self._types[ self.stack[-1] ] in self.subnode_types:
            data = "".join( self.buf )
            data = data.strip()
            self.createData( self.current_path, self.stack[-1], data)

        self.buf = []
        self.stack.pop(-1)
        
        if self.current_path.rfind('.') != -1:
            idx = self.current_path.rfind('.') 
            self.current_path = self.current_path[:idx]

    def characters( self , characters ):
        self.buf.append( characters )
        
    def createData( self, path, type_code, data=_marker):
        factory = self._types[ type_code ]
        if data is not _marker:
            data = factory( data )
        else:
            data = factory()
        last, last_part = traverseStruct( path, self.root  )
        if last_part == 'entry':
            last.append( data )
        else:
            last[ last_part ] = data
            

class ExportWriter( object ):

    _values = {
        types.StringType : "dumpEntry",
        types.IntType : "dumpEntry",
        types.BooleanType : "dumpEntry",
        types.ListType : "dumpList",
        types.TupleType : "dumpList",
        types.DictType : "dumpDictionary"
        }
    
    _attrs = {
        types.StringType : "convertValue",
        types.IntType : "convertValue",
        types.BooleanType : "convertValue",
        }

    _typecode = {
        types.StringType : u"string",
        types.IntType    : u"int",
        types.BooleanType : u"bool",
        types.DictType :  u"dict",
        types.ListType : u"list"
        }

    subnode_types = ( types.ListType, types.DictType, types.TupleType )

    policy_id = u"policy"
    entry_key = u'entry'    
    attributes_key = u'attributes'

    def __init__(self, stream, encoding):
        """
        Set up a serializer object, which takes policies and outputs
        """
        logger = XMLGenerator(stream, encoding)
        self._logger = logger
        self._output = stream
        self._encoding = encoding

        self._logger.startDocument()
        self._stack = []

    def close( self ):
        return
        self._logger.endElementNS((None, self.policy_id), self.policy_id )
        self._logger.endDocument()

    def getValueSerializer( self, v ):
        v_type = type( v )

        serializer_name = self._values.get( v_type )
        if serializer_name is None:
            raise ValueError("invalid type for serialization %r"%v_type)

        method = getattr( self, serializer_name )
        assert isinstance( method, types.MethodType), "invalid handler for type %r"%v_type
        
        return method

    def getAttrSerializer( self, v ):
        v_type = type( v )

        serializer_name = self._attrs.get( v_type )
        if serializer_name is None:
            raise ValueError("invalid type for serialization %r"%v_type)

        method = getattr( self, serializer_name )
        assert isinstance( method, types.MethodType), "invalid handler for type %r"%v_type
        
        return method        

    def getTypeCode( self, v ):

        return self._typecode[ type( v) ]
        
    def dumpDictionary( self, key, value ):

        key = unicode( key )        
        subnodes = []

        type_code = self.getTypeCode( value )
        attr_values = { (None, u'type' ) : type_code }
        attr_names  = { (None, u'type' ) : u'type' }

        for k, v in value.get( self.attributes_key, {}).items():
            k = unicode( k )
            assert not isinstance(v, self.subnode_types )
            serializer = self.getAttrSerializer( v )
            
            attr_values[ (None, k ) ] = serializer( v )
            attr_names[ (None,  k ) ] = k

        
        attrs = AttributesNSImpl( attr_values, attr_names )
        self._logger.startElementNS( ( None, key ), key, attrs )

        for k, v in value.items():
            if k == self.attributes_key:
                continue
            serializer = self.getValueSerializer( v )
            serializer( k, v )

        self._logger.endElementNS( ( None, key ), key )
 
    def dumpList( self, key, value ):
        type_code = self.getTypeCode( value )
        attrs = AttributesNSImpl( { (None, u'type' ) : type_code },
                                  { (None, u'type' ) : u'type' } )
        self._logger.startElementNS( ( None, key ), key, attrs )

        for entry in value:
            serializer = self.getValueSerializer(  entry )
            serializer( self.entry_key, entry )
            
        self._logger.endElementNS( ( None, key ), key )

    def dumpEntry( self, key, value ):
        key = unicode( key )
        type_code = self.getTypeCode( value )
        attrs = AttributesNSImpl( { (None, u'type' ) : type_code },
                                  { (None, u'type' ) : u'type' } )
        self._logger.startElementNS( ( None, key ), key, attrs )
        serializer = self.getAttrSerializer( value )
        self._logger.characters( serializer( value ) )
        self._logger.endElementNS( ( None, key ), key )

    def convertValue( self, value ):
        return unicode( value )


def traverseStruct( path, data, get=False ):
    last = data
    parts = path.split('.')
    parts = filter(None, parts )
    last_part = parts.pop(-1)
        
    for p in parts:
            if p == 'entry':
                last = last[-1]
            else:
                last = last[ p ]

    if get is False:
        return last, last_part

    if last_part == 'entry':
        return last
    else:
        return last[ last_part ]

def mapStruct( data, d=None, prefix='' ):
    if d is None:
        d = dict()
    for k,v in data.items():
        d[prefix+k]=v
        if isinstance( v, (dict, struct) ):
            mapStruct( v, d, prefix+k+'.' )
    return d

def getFactory( ctx, node ):
    product_name = node.attributes['product']
    factory_name = node.attributes['factory']

    if product_name == 'container':
        factory = getattr( ctx, factory_name )
    else:
        factory = getattr( ctx.manage_addProduct[ product_name ], factory_name )
        
    md = dict( node )
    md.update( node.attributes )
    
    if 'product' in md: del md['product']
    if 'factory' in md: del md['factory']

    del md['attributes']

    md = dict( [ (str(k),v) for k,v in md.items() ])
    
    return factory, md


class IOContext( object ):

    def load( self, context ):
        raise NotImplemented

    def construct( self ):
        raise NotImplemented


def CompatiblityFilenameForRule( ctx ):
    # example compatibilty transform
    for i in ctx.key_map['policy.mastering.rules']:
        v = i['filename']
        del i['filename']
        i['extension_expression'] = v


class ImportContext( IOContext ):

    transforms = [
        CompatiblityFilenameForRule
        ]
    
    def __init__( self, context, overrides=None ):
        self.context = context
        self.policy = None
        self.data = None
        self.overrides = overrides or {}

        self.construct_type = None # marker for compatilibity

    def load( self, stream ):

#        if isinstance( stream, str):
#            stream = StringIO.StringIO( stream )
            
        reader = ImportReader()

        parser = make_parser()

        preader = policy_reader.PolicyReader(  parser, u"policy", reader )
        parser.setContentHandler( preader )
        parser.parse( stream )

        if parser.getContentHandler() is preader:
            self.construct_type = 'compatiblity'
            self.data = preader.getPolicy()

        if parser.getContentHandler() is reader:
            
            self.data = reader.getData()
            self.key_map = mapStruct( self.data )        
            for t in self.transforms:
                t( self )

    def construct(self):

        if self.construct_type == 'compatiblity':
            return policy_reader.make_policy( self.context,
                                              self.data,
                                              id = self.overrides.get('id'),
                                              title = self.overrides.get('title') )

        # sort by length, so we finish root config/construction before leaf        
        keys = [ ( len(k), k) for k in self.key_map.keys() ]
        keys.sort()
        keys = [ k[1] for k in keys]
        
        for k in keys:
            handler = self._handlers.get( k )
            if handler is None:
                continue
            data = traverseStruct( k, self.data, get=True )
            handler( self, k, data )

        return self.policy

    def editFromStruct( ctx, name, value ):
        container = ctx.resolveContainer( name )
        container.fromStruct( value )

    def pluginConstructor( ctx, name, value ):
        container = ctx.resolveContainer( name )
        for v in value:
            factory, md = getFactory( container, v )
            factory( **md )
            
    def policyConstructor( ctx, name, value ):
        id = ctx.overrides.get('id')
        if not id:
            id = value.attributes.id
            
        pipeline_id = value.attributes.pipeline_id
        title = value.attributes.get('title', id )
        ctx.policy = ctx.context.addPolicy( id, title, policy_pipeline_id=pipeline_id )

    def resolveContainer( self, name ):
        parts = name.split('.')
        parts.reverse()

        for p in parts:
            accessor = self._names.get( p )
            if accessor is not None:
                if isinstance( accessor, str):
                    accessor = getattr( self.policy, accessor )
                else:
                    accessor = lambda func=accessor, policy=self.policy: func(policy)
                return accessor()

    # plugin container accessors, callable to be called with policy, or string method spec of policy
    _names = {'identification':'getContentTransforms',
              'mastering' : 'getContentMastering',
              'organization' : 'getContentOrganization',
              'rules' : 'getContentRules',
              'resolver' : 'getDeploymentURIs',
              'transports' :'getContentDeployment',
              'sources' : lambda policy: policy.getContentIdentification().sources,
              'filters' : lambda policy: policy.getContentIdentification().filters,
              'site_resources': 'getSiteResources'}


    # just a calllable accepting ( policy, name, value )
    _handlers = {
        'policy.identification.sources' : pluginConstructor,
        'policy.identification.filters' : pluginConstructor,
        'policy.organization' : editFromStruct,
        'policy.transports' : pluginConstructor,
        'policy.site_resources': pluginConstructor,
        'policy.mastering.rules' : pluginConstructor,
        'policy.mastering' : editFromStruct,
        'policy.resolver'  : editFromStruct,
        'policy': policyConstructor,
        }


class ExportContext( object ):

    def load( self, policy ):
        self.policy = policy

    def construct( self, stream=None):
        stream = StringIO.StringIO()
        serializer = ExportWriter( stream, "utf-8")
        info = self.policy.getInfoForXml()
        serializer.dumpDictionary( "policy", info ) 
            
        serializer.close()
        return stream.getvalue()



#################################
# pull some fixes from python stdlib for 2.3
import codecs

def _outputwrapper(stream,encoding):
    writerclass = codecs.lookup(encoding)[3]
    return writerclass(stream)

if hasattr(codecs, "register_error"):
    def writetext(stream, text, entities={}):
        stream.errors = "xmlcharrefreplace"
        stream.write(escape(text, entities))
        stream.errors = "strict"
else:
    def writetext(stream, text, entities={}):
        text = escape(text, entities)
        try:
            stream.write(text)
        except UnicodeError:
            for c in text:
                try:
                    stream.write(c)
                except UnicodeError:
                    stream.write(u"&#%d;" % ord(c))

def writeattr(stream, text):
    countdouble = text.count('"')
    if countdouble:
        countsingle = text.count("'")
        if countdouble <= countsingle:
            entities = {'"': "&quot;"}
            quote = '"'
        else:
            entities = {"'": "&apos;"}
            quote = "'"
    else:
        entities = {}
        quote = '"'
    stream.write(quote)
    writetext(stream, text, entities)
    stream.write(quote)
    

class XMLGenerator( XMLGenerator ):
    # subclass to bring 2.4 fixes to 2.3
    
    def startElementNS(self, name, qname, attrs):
        if name[0] is None:
            name = name[1]
        elif self._current_context[name[0]] is None:
            # default namespace
            name = name[1]
        else:
            name = self._current_context[name[0]] + ":" + name[1]
        self._out.write('<' + name)

        for k,v in self._undeclared_ns_maps:
            if k is None:
                self._out.write(' xmlns="%s"' % (v or ''))
            else:
                self._out.write(' xmlns:%s="%s"' % (k,v))
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            if name[0] is None:
                name = name[1]
            elif self._current_context[name[0]] is None:
                # default namespace
                #If an attribute has a nsuri but not a prefix, we must
                #create a prefix and add a nsdecl
                prefix = self.GENERATED_PREFIX % self._generated_prefix_ctr
                self._generated_prefix_ctr = self._generated_prefix_ctr + 1
                name = prefix + ':' + name[1]
                self._out.write(' xmlns:%s=%s' % (prefix, quoteattr(name[0])))
                self._current_context[name[0]] = prefix
            else:
                name = self._current_context[name[0]] + ":" + name[1]
            self._out.write(' %s=' % name)
            writeattr(self._out, value)
        self._out.write('>')

# end py2.3 compat
###############

if __name__ == '__main__':
   
   d = {'identification':{'filters':[ { 'attributes': {'id':'no_members', 'expr':'python: not 1'}} ] },
        'bd':True,
        'ed':False,
        'ef':"ste",
        'xy':[1,2,3,4],
        "ze":{'fa':1,
              'ze':['a','b']}
        }

   from pprint import pprint
   from StringIO import StringIO
   from xml.dom.minidom import parseString
   
   stream = StringIO()
   serializer = ExportWriter( stream, "utf-8")
   try:
       serializer.dumpDictionary('identification', d )
   except:
       import sys, pdb, traceback
       exc_info = sys.exc_info()
       traceback.print_exception( *exc_info )
       pdb.post_mortem( exc_info[-1] )       
   serializer.close()

   xstr =  stream.getvalue()
   mdom = parseString( xstr )

   print mdom.toprettyxml()
   
   parser = make_parser()
   reader = ImportReader()
   parser.setContentHandler(reader)

   stream = StringIO( xstr )
   try:
       parser.parse( stream )
   except:
       import sys, pdb, traceback
       exc_info = sys.exc_info()
       traceback.print_exception( *exc_info )
       pdb.post_mortem( exc_info[-1] )
   data = reader.getData()
   pprint(data)

   print
   print

   key_map = mapStruct(data)
   keys = [ ( len(k), k) for k in key_map.keys() ]
   keys.sort()
   keys = [ k[1] for k in keys]
   for k in keys:
       print k, key_map[k]


    
