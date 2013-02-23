from Products.CMFDeployment.incremental import getIncrementalIndexId
from Products.CMFCore.utils import getToolByName
from core import PipeSegment

class DeletionSegment( PipeSegment ):

    def process( self, pipeline, descriptor ):
        storage = pipeline.services['ContentStorage']
        organization = pipeline.services['ContentOrganization']
        dependencies = pipeline.services['ContentDependencies']

        path = organization.getContentPathFromDescriptor( record )
        storage.remove( descriptor )


class RecordDeployment( PipeSegment ):

    policy_idx = None

    def process( self, pipeline, descriptor ):

        idx = self.getPolicyIndex( pipeline )
        idx.recordObject( descriptor.rule_id, descriptor.getContent() )

        return descriptor

    def getPolicyIndex( self, pipeline ):

        if self.policy_idx is not None:
            return self.policy_idx

        policy = pipeline.services['DeploymentPolicy']        
        catalog = getToolByName( policy, 'portal_catalog')
        indexes = catalog.getIndexObjects()

        pidx_id = getIncrementalIndexId( policy )

        for idx in indexes:
            if idx.getId() == pidx_id:
                self.policy_idx = idx
                return self.policy_idx

        raise AttributeError( pidx_id )
        
        

        

        
        
