"""
$Id: environment.py 1202 2006-03-04 08:41:52Z hazmat $
"""

from Products.CMFDeployment.Descriptor import DescriptorFactory
from core import PipeSegment
from storage import ContentStorage

class PipeEnvironmentInitializer( PipeSegment ):

    __implements__ = ( PipeSegment )

    def process( self, pipe, ctxobj ):
        self.setupServices( pipe, ctxobj )
        self.setupVariables( pipe, ctxobj )
        self.setupURIResolver( pipe, ctxobj )
        return ctxobj
    
    def setupVariables( self, pipe, ctxobj ):

        dfactory = DescriptorFactory( ctxobj )
        pipe.services["DescriptorFactory"] = DescriptorFactory

        organization = pipe.services['ContentOrganization']
        mount_point = organization.getActiveStructure().getCMFMountPoint()
        mount_path = mount_point.getPhysicalPath()
        mlen = len('/'.join(mount_path))

        pipe.variables['mount_length'] = mlen
        

    def setupURIResolver( self, pipe, ctxobj ):

        resolver = pipe.services['ContentResolver']
        uri_resolver = resolver.clone( persistent = 0 )

        organization = pipe.services['ContentOrganization']
        mount_point = organization.getActiveStructure().getCMFMountPoint()
        mount_path = mount_point.getPhysicalPath()
        mlen = len('/'.join(mount_path))
        mount_url_root = mount_point.absolute_url(1)

        # should setup an edit method for this
        uri_resolver.mount_path = mount_url_root
        uri_resolver.source_host = ctxobj.REQUEST['SERVER_URL']
        uri_resolver.mlen = mlen

	uri_resolver.setupExternalResolver()

        pipe.services['ContentResolver'] = uri_resolver
        
        
    def setupServices( self, pipe, ctxobj ):
        addService = pipe.services.__setitem__

        source     = ctxobj.getContentIdentification()
        addService("ContentIdentification", source)
        
        structure  = ctxobj.getContentOrganization()
        addService("ContentOrganization", structure)
        
        mastering  = ctxobj.getContentMastering()
        addService("ContentRules", mastering)
        
        deployer   = ctxobj.getContentDeployment()
        addService("ContentTransports", deployer)
        
        resources = ctxobj.getSiteResources()
        addService("SiteResources", resources)

        resolver   = ctxobj.getDeploymentURIs()
        addService("ContentResolver", resolver )
        
        history    = ctxobj.getDeploymentHistory()
        addService("ContentHistory", history )

        addService("ContentStorage", ContentStorage() )

        transforms = ctxobj.getContentTransforms()
        addService("ContentTransforms", transforms)

        addService("DeploymentPolicy", ctxobj )
