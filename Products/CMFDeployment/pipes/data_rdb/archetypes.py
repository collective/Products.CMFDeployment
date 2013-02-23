"""
dump an entire plone site into a relational database.

 including all schema attributes.

 include relations


relation support is a little on the weak side, archetypes
supports many rich semantics here, bidirectional many 2 many,
with code hooks for further constraint definition, as done for example
in the Relations product.

we create by default all relations as a many 2 many mapping, with
a separate join table for each relation, with two columns, the source uid and
the target uid, the source uid points back to the originating schema's
portal type table,  the target uid is more unconstrained and we point
it a master identity table which contains all uids in the system, along
with table information to allow for unambigiously locating the exact
row of the target object, as by default the target object could be
in one of any many number of tables.


futures..

 - hierarchy modeling via adjaency list impl in sa
 - if relation is constrained to a single target type, we could
   concievably do a nice many to many relation directly against
   the target's table.
 - should test with postgres


----------- sa notes ----

default method having access to object

proxy engines --.. carry over engine values?

relations want real engine access. proxy does not suffice.

sa is really overly forgiving about putting junk in relations properties

sa could really use some a delete on cascade option

it would be nice if the dependency system could handle table creation as well

ditto on making an engine option for create_tables_or_replace, create_tables_if_needed
or something like that.

all the repr tricks are evil, and cause crashes in pdb if the internal state
isn't right.

i'm either running into acquisiton bug around acquiring UID or SA is having
trouble somewhere distinguishing an insert from an upate?.. when the per object
called to getIdentity in the serializer is restored, a primary key violation
on the object_identity table is generated.

-----------

references

  reference

  object table
  oid | portal_type | table_name

  relation table -
  s oid |  t oid  | relation

author: kapil thangavelu <hazmat@objectrealms.net>
  
"""

from mx.DateTime import DateFromTicks
from sqlalchemy.util import OrderedDict
import sqlalchemy as rdb

from DateTime import DateTime

from Products.Archetypes import public as atapi
from Products.CMFCore.utils import UniqueObject
from Products.CMFDeployment.segments.core import Consumer


# external method tests

def dump_schema( self, db_uri="postgres://database=tat" ):

    # setup up the schema definitions
    engine = rdb.create_engine( db_uri, echo=True )

    # connect to database
    schema_model = ArchetypesSchemaModel( engine )

    # load up schemas
    for archetype_info in self.archetype_tool.listRegisteredTypes( inProject=True):
        schema_model.loadType( archetype_info['klass'], context=self )

    # create table as needed
    schema_model.createTables()
    return "Schema Created"
    # dump content transactionally (indie)
    try:
        dump_content( self, schema_model )
    except:
        import pdb, sys, traceback
        ec, e, tb = sys.exc_info()
        print ec, e
        traceback.print_tb( tb)
        pdb.post_mortem( tb )
        engine.rollback()
        rdb.objectstore.clear()        
        raise e
    
    engine.commit()
    return "Success"


def dump_content( self, model ):
    # dump content
    for brain in self.portal_catalog():
        content = brain.getObject()
        
        if content is None: continue
        elif isinstance( content, UniqueObject): continue

        peer = model.saveObject( content )
    rdb.objectstore.commit()



# requires corresponding engine.generator changes
class ForeignKeyWithAction( rdb.ForeignKey ):
    
    allowed_change_actions = ( None,
                              'restrict',
                              'cascade',
                              'set null',
                              'set default', )
    
    def __init__(self, column, on_delete=None, on_update=None):

        rdb.ForeignKey.__init__( self, column )

        self.on_delete = self.on_update = None
        
        if on_delete:
            assert on_delete in self.allowed_change_actions
            self.on_delete = "ON DELETE %s"%on_delete

        if on_update:
            assert on_update in self.allowed_change_actions            
            self.on_update = "ON UPDATE %s"%on_update
    

class ListType( rdb.TypeDecorator, rdb.String ):

    def convert_bind_param( self, value, engine):
        if value is None:
            return None
        return "\n".join( value )

    def convert_result_value( self, value, engine):
        return value.split("\n")

class BooleanType( rdb.TypeDecorator, rdb.Boolean ):

    def convert_bind_param( self, value, engine ):
        if value is None: return None
        return bool( value )

    def convert_result_value( self, value, engine ):
        return value

class DateType( rdb.TypeDecorator, rdb.DateTime ):

    def convert_bind_param( self, value, engine ):
        if value is None:
            return None
        if isinstance( value, DateTime ):
            value = DateFromTicks( DateTime.timeTime() )

        # psycopg1 specific hack
        if hasattr( engine, 'version') and engine.version == 1:
            return engine.module.TimestampFromMx( value )

        return value


class ArchetypesFieldTranslator( object ):

    def __init__( self, generator, table_name ):
        self.generator = generator
        self.table_name = table_name
        
    def ident_translate( identifier ):
        return identifier.lower().replace(' ', '_')

    ident_translate = staticmethod( ident_translate )

    def getDefaultArgs( self, field, use_field_default=False ):
        args = []
        if use_field_default and field.default:
            args.append( rdb.PassiveDefault( field.default ) )
        kwargs = {
            'nullable' : not field.required,
            'key' : field.getName(),            
            }
        return args, kwargs
     
    # hack around some objects with bad metadata fields.
    field_overrides = {('allowDiscussion', 'StringField'):'visit_BooleanField'}

    def visit( self, field ):
        field_visitor = "visit_%s"%( field.__class__.__name__ )
        visitor = getattr( self, field_visitor, None )
        if visitor is None:
            print "No Visitor", field_visitor, field.getName()
            return None

        override_key = (field.getName(), field.__class__.__name__)
        if override_key in self.field_overrides:
            visitor = getattr( self, self.field_overrides[override_key] )
        
        return visitor( field )
    
    def visit_StringField( self, field ):
        
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )
            
        return rdb.Column(
            self.ident_translate( field.getName() ),
            rdb.String(4000),
            *args,
            **kwargs )

    visit_TextField = visit_StringField

    def visit_LinesField( self, field ):
        
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )
            
        return rdb.Column(
            self.ident_translate( field.getName() ),
            ListType(4000),
            *args,
            **kwargs )

    def visit_FileField( self, field ):
        args, kwargs = self.getDefaultArgs( field )

        return rdb.Column(
            self.ident_translate( field.getName() ),
            rdb.Binary(),
            *args,
            **kwargs)

    visit_ImageField = visit_FileField
    visit_PhotoField = visit_FileField

    def visit_BooleanField( self, field ):
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )

        return rdb.Column(
            self.ident_translate( field.getName() ),
            BooleanType(),
            *args,
            **kwargs )

    def visit_IntegerField( self, field ):
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )

        return rdb.Column(
            self.ident_translate( field.getName() ),
            rdb.Integer(),
            *args,
            **kwargs )

    def visit_FloatField( self, field ):
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )

        return rdb.Column(
            self.ident_translate( field.getName() ),
            rdb.Float(),
            *args,
            **kwargs )        

    def visit_FixedPointField( self, field ):
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )
        return rdb.Column(
            self.ident_translate( field.getName() ),
            rdb.Numeric( precision = field.precision ),
            *args,
            **kwargs )

    def visit_DateTimeField( self, field ):
        args, kwargs = self.getDefaultArgs( field, use_field_default=True )
        return rdb.Column(
            self.ident_translate( field.getName() ),
            DateType(),
            *args,
            **kwargs )            

    def visit_ReferenceField( self, field ):
        table = rdb.Table(
            "%s_%s"%(self.table_name, self.ident_translate( field.getName() )),
            self.generator.engine,
            rdb.Column('source',
                   rdb.String(50),
                   ForeignKeyWithAction('%s.uid'%self.table_name, on_delete='cascade'),
                   nullable=False),
            rdb.Column('target',
                   rdb.String(50),
                   ForeignKeyWithAction('object_identity.uid', on_delete='cascade'),
                   nullable=False)
            )


        table.reference_name = self.ident_translate( field.getName() )
        return table

class ArchetypeSerializer( object ):

    def __init__(self, schema_map):
        self.schema_map = schema_map

    def saveObject( self, content ):
        peer_factory = self.schema_map[ content.portal_type ]
        if peer_factory is None:
            print "no factory for", content.portal_type
            return

        peer = peer_factory.get( uid=content.UID() ) or peer_factory()
        
        for field in content.Schema().fields():

            table_name = self.schema_map.ident_translate( content.portal_type)
            field_name = field.getName()
            
            value = field.getAccessor( content )( )

            if isinstance(field, atapi.ReferenceField):
                if not value:
                    continue
                
                peer_relation = getattr( peer, field_name, None )
                
                if peer_relation is None:
                    raise RuntimeError( "invalid peer relation for %s"%field_name )
                
                if not field.multiValued: # or not isinstance( value, (list, tuple))::
                    ob_ident = self.getIdentityFor( value )
                    peer_relation.append( ob_ident )
                    continue
                
                for ob in value:
                    ob_ident = self.getIdentityFor( value )
                    peer_relation.append( ob_ident )

                continue
            
            if field.required and value is None:
                value = field.getDefault( content )
                
            if isinstance(field, atapi.DateTimeField) and value is not None:
                value = DateFromTicks( value.timeTime() )
                
            setattr( peer, field_name, value )
                     

        # and now for the primary key and identity tables
        setattr( peer, 'uid', content.UID())

        assert peer.uid is not None

        #identity = self.getIdentityFor( content )

        return peer

    def deleteObject( self, content ):
        peer_factory = self.schema_map[ content.portal_type ]

        identity = self.getIdentityFor( content, create=False )
        if identity is not None:
            identity.delete( uid=content.UID() )
        peer_factory.delete( uid=content.UID() )
        
    def getIdentityFor( self, content, create=True ):
        identity_factory = self.schema_map.getIdentityKlass()
        identity = identity_factory.get( content.UID() )
        if identity is not None or not create:
            return identity

        identity = self.schema_map.createIdentity()
        setattr( identity, 'uid', content.UID() )
        setattr( identity, 'id',  content.getId() ),
        setattr( identity,
                 'table_name',
                 self.schema_map.ident_translate( content.portal_type ) )

        return identity
        
class ArchetypesSchemaModel( object ):

    translator_factory = ArchetypesFieldTranslator
    serializer_factory = ArchetypeSerializer
    
    def __init__(self, engine=None):
        self._tables = OrderedDict()
        self._peer_factories = {}
        
        self.engine = engine or ProxyEngine()
        self.generateDefaults()

        self.serializer = self.serializer_factory( self )

        # rebind
        self.ident_translate = self.translator_factory.ident_translate
        self.saveObject = self.serializer.saveObject
        self.deleteObject = self.serializer.deleteObject
        
    def __getitem__(self,key):
        return self._peer_factories.get( key )

    def createTables(self):
        for table in self._tables.values():
            table.create()

    def createIdentity(self):
        return self._peer_factories[ self._identity ]()

    def getIdentityKlass(self):
        return self._peer_factories[ self._identity ]

    def generateDefaults( self ):
        self._identity = "object_identity"        
        object_identity = rdb.Table( self._identity,
                                 self.engine,
                                 rdb.Column( "uid", rdb.String(50), primary_key=True ),
                                 rdb.Column( "id",  rdb.String(60) ),
                                 rdb.Column( "table_name", rdb.String(50) )
                                 )

        class ObjectIdentity( object ): pass
        rdb.assign_mapper( ObjectIdentity, object_identity )
        self._tables[ self._identity ] = object_identity
        self._peer_factories[ self._identity ] = ObjectIdentity

    def loadType( self, archetype_klass, context):

        if archetype_klass.portal_type in self._tables:
            return

        # check if its a tool content type, if so ignore
        if issubclass( archetype_klass, UniqueObject):
            return
        
        instance = archetype_klass('fake_instance')
        instance._at_is_fake_instance = True
        instance._is_fake_instance = True
        wrapped = instance.__of__( context )
        wrapped.initializeArchetype()

        self._loadInstance( instance )
        
        # just to be sure
        instance.unindexObject()

    def _loadInstance( self, instance ):

        relation_tables = []
        primary_columns = [ rdb.Column( "uid", rdb.String(50), primary_key=True ) ]
        
        portal_type = instance.portal_type
        
        table_name = self.ident_translate( portal_type )
        field_translator = self.translator_factory( self, table_name )
        

        print "Processing Type", portal_type

        d = {}
        for field in instance.Schema().fields():
            # filter badness from fields with same speling but different captilization.
            field_name = self.ident_translate( field.getName() )
            if field_name in d:
                continue

            result = field_translator.visit( field )

            if result is None:
                continue
            elif isinstance( result, rdb.Column):
                primary_columns.append( result )
            elif isinstance( result, rdb.Table ):
                relation_tables.append( result )
            else:
                print "Unexpected", result
                raise RuntimeError

            d[field_name] = None


        # define type primary table
        type_table = rdb.Table( table_name,
                                self.engine,
                                *primary_columns )
                                

        # setup a peer factory
        klass_name = "%s_serializer"%portal_type.lower().replace(' ', '_')
        type_klass = type( klass_name, (object,), {} )

        self._peer_factories[ portal_type ] = type_klass
        self._tables[ portal_type ] = type_table


        # setup the reference relations
        identity = self._peer_factories[ self._identity ]
        properties = {}
        for relation_table in relation_tables:
            print "reference name", relation_table.reference_name

        for relation_table in relation_tables:
            properties[ relation_table.reference_name ] = rdb.relation( identity.mapper, relation_table, lazy = False)            
            self._tables[ relation_table.name ] = relation_table

        kwargs = {'properties':properties}

        # associate peer to mapper
        rdb.assign_mapper( type_klass, type_table, **kwargs )



        
class RDBStorageManager( object ):

    def add( self, pipe, descriptor ):
        if descriptor.isGhost():
            return
        content = descriptor.getContent()
        model = pipe.variables['rdb_model']
        model.saveObject( content )

    def remove( self, pipe, descriptor ):
        model = pipe.variables['rdb_model']
        model.deleteObject( content )

class RDBStorage( Consumer, RDBStorageManager ):

    process = add

class RDBRemoval( Consumer, RDBStorageManager ):

    process = remove        
        
