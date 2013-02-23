"""
ROUGH DRAFT

defines the operation of the incremental pipeline for deployment.

deploying content on an incremental basis is a straight forward though
complex process. the naive initial implementation in cmfdeployment 1.0,
merely deployed content created/modified since the last deployment
run. real world experience quickly proved this to be fatally flawed for
a number of reasons.

  - content often have interdependencies that need to be modeled
    in an incremental deployment system.

  - the engine needed to process content deletions, previously the
    deployment engine dealt only with publishing.


the incremental engine uses the following components, arranged as shown
in the diagram of an execution pipeline below.

  Dependency Manager

   Responsible for processing a descriptor's specified dependencies
   and reverse dependencies to ensure their included in the deployment.

  IncrementalPolicyIndex

   A plugin zcatalog index, installed into the portal catalog, and used
   to track when a deployed piece of content is deleted, and then
   adds a deletion record to the policy's deletion source [below]

  Plugin Content Sources

   AlwaysDeployed Source

    returns content marked to be deployed every run. 

   Deletion Source

    a content source for deletion records.

   Dependency Source

    a source for dependencies, as injected by the dependency manager.

   the dependency plugin content source is injected to during
   the pipeline execution. a duplicate eliminating filter needs
   to be utilized in the pipeline execution ( earlier the better ).

  Pipeline Invariant
  
    - deployed content filtered out will trigger deletion descriptor
      creation.

 ------

 Incremental Pipeline Diagram 

 Content Sources --<                  catalog | deletions | dependencies
     +                                             +              +
     +                                             +              +
  Filters                                          +              + 
     +                                             +              +
     +                                             +              +
  Content Rules                                    +              +
     +                                             +              +
     +                                             +              +
  Dependency Manager  ---------------------------------------------
     +                                             +
     +                                             +
  Resolver                                         +
     +                                             +
     +                                             +
  ContentMap -----------------------------IncrementalIndex
  

Todo

 - api for cleaning state from a descriptor [ and children ]
   to make ready for serialization.

     
$Id: incremental.py 1957 2007-05-14 07:26:27Z hazmat $
"""


from Namespace import *
from BTrees.Length import Length
from BTrees.IOBTree import IOBTree

#KW: Old import
#from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
from Products.PluginIndexes.interfaces import IPluggableIndex
from zope.interface import implements

import DefaultConfiguration
from Descriptor import DescriptorFactory
from ExpressionContainer import getDeployExprContext
from utils import unwrap_object

#################################
# pipeline processing of deletion records
#
#  - get and inject dependencies into queue
#
#  - remove from resolver
#
#  - remove from storage


class DeletionRecord( object ):
    """
     models a content record ..

     really a deletion descriptor, but supporting just enough descriptor
     api to be processed by deletion pipeline and its components.

     -- uri resolver

      - getdescriptors
      - getSourcePath or content_url

      
     -- dependencies
     
      - getReverseDependencies


     -- storage

      - structure.getContentPathFromDescriptor( desc )

        - content_path or getContent/getPhysicalPath :-(
      
      - getFileName
      
    """

    # class defaults for new variables
    rule_id = None
    content_type = 'n/a'
    content_title = 'n/a'
    deleted_by = 'n/a'
    deletion_time = None
    
    def __init__(self, policy, descriptor ):

        content = descriptor.getContent()
        
        self.content_id = content.getId()
        self.content_url = descriptor.getContentURL()
        self.content_type = content.portal_type
        self.content_title = content.Title()
        self.deleted_by = getSecurityManager().getUser().getId()
        self.deletion_time = DateTime()
        self.file_name = descriptor.getFileName()

        # lazy inits.. 
        self.dependency_rids = None
        self.child_descriptors = None
        
        # attach child descriptors
        for cd in descriptor.getContainedDescriptors(include_self=False):
            if self.child_descriptors is None:
                self.child_descriptors = []
            self.child_descriptors.append( DeletionRecord( policy, cd ) )

        # serialize dependencies
        dependencies = descriptor.getReverseDependencies()
        
        for dep in dependencies:
            if self.dependency_rids is None:
                getrid = getToolByName( content, 'portal_catalog').getrid
                self.dependency_rids = []
            rid = getrid( "/".join( dep.getPhysicalPath() ) )
            if rid is None: 
                continue
            self.dependency_rids.append( rid )

        # get deployed to path
        organization = policy.getContentOrganization()
        self.content_path = organization.getActiveStructure().getContentRelativePath( content )


    def getContentPath(self):
        return self.content_path

    def getSourcePath(self): # utilized by dv remapping, not of interest yet for content
        return None

    def getFileName(self):
        return self.file_name

    def getAliases(self):
        return ()
    
    def getDescriptors(self):
        if not self.child_descriptors:
            return [ self ]
        else:
            return (self,)+tuple(self.child_descriptors)

    # deletion descriptors store nested descriptors in a flat list
    getContainedDescriptors = getDescriptors

    def getReverseDependencies( self, context ):

        if not self.dependency_rids:
            raise StopIteration
        
        catalog = getToolByName( context, 'portal_catalog')        
        
        for drid in self.dependency_rids:
            try:
                dpath = catalog.getpath( drid )
            except KeyError: # dependency has gone by bye
                continue
            dep = catalog.resolve_path( dpath )
            if dep is not None:
                yield dep


def getIncrementalIndexId( policy ):
    pid = policy.getId()
    iid = "%s-policy_idx"%pid
    return iid

def getIncrementalIndex( policy ):
    portal_catalog = getToolByName( policy, 'portal_catalog')
    catalog = portal_catalog._catalog
    iid = getIncrementalIndexId( policy )
    if not iid in portal_catalog.indexes():
        raise AttributeError( iid )
    return catalog.getIndex( iid )
    

addPolicyIncrementalIndexForm = DTMLFile('ui/IncrementalIndexForm', globals())

class PolicyIncrementalIndex( SimpleItem ):
    """
    abuses the catalog plugin index interface to get events for content
    deletion also stores the info re the set of objects deployed by the
    corresponding policy.
    """
    
    meta_type = "Policy Incremental Index"
    
    #KW: __implements__ = PluggableIndexInterface
    implements(IPluggableIndex)

    manage_options = (

        {'label':'Overview',
         'action':'index_overview'},

        {'label':'Index',
         'action':'idx/manage_workspace'}

        )

    security = ClassSecurityInfo()

    index_overview = DTMLFile('ui/IncrementalIndexView', globals())    

    def __init__(self, id, extra=None, caller=None):
        self.id = id
        self.policy_id = self._getPolicyId( id )

        self.clearState()


    def getId(self):
        return self.id

    def getEntryForObject( self, documentId, default=None):
        return self._index.get( documentId, default )

    def index_object( self, documentId, obj, threshold=None):
        # policy execution directly populates through the
        # recordObject api.

        # this implementation focuses on checking whether an
        # object is already deployed, and if it is then we check
        # whether or not it still matches to a content rule
        # if doesn't then we create a deletion record for it.

        # in order to process workflow changes, the policy index id
        # needs to be added as a dummy workflow variable.

        # note of caution filters operate out of band from this...
        # XXX for completeness we should do filter matching as well.

        if not self._index.has_key(documentId):
            return 1
        obj = unwrap_object( obj )
        policy = self._getPolicy()
        deletion_source = policy._getOb( DefaultConfiguration.DeletionSource, None )
        if deletion_source is None: # XXX log me
            return 1

        portal = getToolByName( self, 'portal_url').getPortalObject()
        ctx = getDeployExprContext( obj, portal )

        match_found = None
        rules = policy.getContentMastering().rules
        for rule in rules.objectValues():
            if rule.isValid( obj, ctx):
                match_found = rule
                break

        if match_found is not None:
            return 1

        self._processDeletion( policy, rules, deletion_source, documentId, obj, ctx)
        return 1


    def unindex_object( self, documentId):
        # we get unindex call backs on renames and moves as well
        # which is fine since that also requires generating a deletion
        # record for the old content location for static deployments..
        # for data deployments this might be a little more tricky, since
        # we might not want the deletion, and we might have relational
        # referential integrity to deal with as well, this actually
        # references another scenario where the deletion index is inadequate
        # namely workflow state change won't trigger a full reindex, hmmm..
        # worst case is a dummy variable to the workflows matching this idx
        # and check during index if the object is still deployable, and if
        # not remove it from the index and create a deletion record.

        if not self._index.has_key(documentId):
            return
        policy = self._getPolicy()
        deletion_source = policy._getOb( DefaultConfiguration.DeletionSource, None )
        if deletion_source is None:
            # XXX log me
            return
        
        content = self.getObjectFor( documentId )
        rules = policy.getContentMastering().rules
        self._processDeletion( policy, rules, deletion_source, documentId, content )

    def _apply_index( request, cid=""):
        return None

    def numObjects(self):
        return self._length()

    def __len__(self):
        return self._length()

    def indexSize(self):
        return self._length()

    def clear(self):
        # i can't do that jim ;-)
        return

    #################################
    def _getPolicyId( self, id ):
        idx = id.rfind('-')
        return id[:idx]
    
    def _getPolicy(self): 
        dtool = getToolByName( self, 'portal_deployment')
        policy = dtool._getOb( self.policy_id )
        return policy

    def _processDeletion( self, policy, rules, deletion_source, documentId, content, ctx=None ):
        # all of this seems a little expensive for inline to index/unindex

        factory = DescriptorFactory( policy )
        descriptor = factory( content )

        rule_id, path = self._index[ documentId ]
        rule = rules._getOb( rule_id, None )
        if rule is None:
            # try to find any matching rule
            #print "XXX", "Rule not found", rule_id
            mastering = policy.getContentMastering()
            if not mastering.prepare( descriptor ):
                print "XXX"*2, "Can't process deletion"
                return
        else:
            # we know which rule to use
            if ctx is None:
                portal = getToolByName( policy, 'portal_url').getPortalObject()
                ctx = getDeployExprContext( content, portal )
            rule.process( descriptor, ctx )

        record = DeletionRecord( policy, descriptor )
        record.rule_id = rule.getId()

        deletion_source.addRecord( record )
        
        del self._index[documentId]
        self._length(-1)


    #################################
    
    def getObjectFor( self, documentId ):
        return self.getobject( documentId )

    security.declarePrivate('recordObject')
    def recordObject(self, rule_id, object):
        assert rule_id is not None
        catalog = self.aq_parent
        path = '/'.join( object.getPhysicalPath() )
        key = catalog.uids.get( path, None )
        
        if key is None:
            # don't create persistent records for objects not in catalog
            return 

            # not sure if we should do this.. at min log this
            # basically index the object if no rid is found for it.
            pcatalog = getToolByName(self, 'portal_catalog')
            pcatalog.indexObject( object )

            key = catalog.uids.get( path )
            assert key is not None, "path has no key %s"%(path)
  
        if not self._index.has_key( key ):
            self._length.change(1)
            self._index[ key ] = ( rule_id, path )
        else:
            srule_id, spath = self._index[ key ]
            if rule_id != srule_id or spath != path:
                self._index[key] = ( rule_id, path )
                

    security.declarePrivate('clearState')
    def clearState(self):
        self._length = Length(0)
        self._index  = IOBTree()
        
InitializeClass( PolicyIncrementalIndex )
