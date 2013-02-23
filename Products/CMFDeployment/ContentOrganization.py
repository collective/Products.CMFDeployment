##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
# All Rights Reserved
#
# This file is part of CMFDeployment.
#
# CMFDeployment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFDeployment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
Purpose: Organizes Content in a Deployment Target Structure
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: ContentOrganization.py 1398 2006-06-27 19:02:51Z hazmat $
"""
from __future__ import nested_scopes
from os import sep
from Namespace import *
from structure import RootDirectory, descendant_filtered_folder_collector as\
     folder_collector
from DeploymentExceptions import InvalidCMFMountPoint, InvalidPortalType

from Products.CMFDeployment import DeploymentProductHome
from Products.CMFCore.utils import getToolByName
from Log import LogFactory

log = LogFactory('Organization')

class ContentOrganization(Folder):
    """
    originally intended as a gateway to different structure
    implementations
    """
    
    meta_type = 'Content Organization'

    security = ClassSecurityInfo()

    manage_options = (
        
        {'label':'Overview',
         'action':'overview'},
        
        {'label':'FS Mount',
         'action':'structure/filesystem_mount'},

        {'label':'CMF Mount',
         'action':'structure/cmf_mount_form'},        

        {'label':'Restricted',
         'action':'structure/restricted_form'},

        {'label':'Composites',
         'action':'structure/composites_form'},

        {'label':'Policy',
         'action':'../overview'}
        )

    overview  = DTMLFile('ui/ContentOrganizationOverview',  globals())

    xml_key = 'organization'

    def __init__(self, id):
        self.id = id

    security.declarePrivate('getActiveStructure')
    def getActiveStructure(self):
        return self.structure
                                  
    security.declarePrivate('mount')
    def mount(self):
        structure = self.getActiveStructure()
        structure.mount()

    security.declarePrivate('unmount')
    def unmount(self):
        structure = self.getActiveStructure()
        structure.unmount()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        if self._getOb( 'structure', None ) is None:
            self._setObject('structure',CMFContentStructure('structure'))
        #self._setObject('organize', StructureMapping('organize'))

    def getContentPath(self, content ):
        return self.getActiveStructure().getContentPath( content )

    def getContentRelativePath( self, content ):
        return self.getActiveStructure().getContentRelativePath( content )

    def getContentPathFromDescriptor( self, descriptor ):
        return self.getActiveStructure().getContentPathFromDescription( descriptor )

    security.declarePrivate('getInfoForXml')
    def getInfoForXml( self ):
        structure = self.getActiveStructure()
        
        return {'attributes':{ 'cmf_path':structure.cmf_mount_point,
                               'fs_path':structure.mount_point },
                'restricted': list( structure.restricted ),
                'composites': list( structure.composite_doc_types ),

                                    }

    security.declarePrivate('fromStruct')
    def fromStruct( self, struct ):
        structure = self.getActiveStructure()
        structure.setRestrictedPoints( struct.get('restricted', () ) )
        structure.setCMFMountPoint( struct.attributes.cmf_path )
        fs_path = struct.attributes.fs_path
        
        if fs_path.startswith('*'):
            # make default paths play nice with platform specific paths
            fs_path = sep.join( fs_path.split('/') )
            fs_path = fs_path.replace( '*', DeploymentProductHome )
            
        structure.setMountPoint( fs_path )

InitializeClass(ContentOrganization)

class CMFContentStructure(RootDirectory):

    meta_type = 'CMF ContentStructure'

    manage_options = (
                
        {'label':'Organization',
         'action':'../overview'},
        
        {'label':'Policy', 
         'action':'../../overview'}  

        )

    cmf_mount_form = DTMLFile('ui/CMFMountForm', globals())
    restricted_form = DTMLFile('ui/OrganizationRestrictedForm', globals())
    composites_form  = DTMLFile('ui/OrganizationCompositeForm', globals())
    
    cmf_mount_point = '/'
    restricted = ('acl_users', 'content_type_registry')
    composite_doc_types = ()
    
    def mount(self):
        """
        we descend into the cmf object structure collecting
        folder like objects, we filter them according to
        the following lambda, which we use to get remove
        things that are infrastructure specific.

        using the collected folders, we create an object structure
        that mirrors the layout of the collection.
        this object/container structure is then written/mirrored
        to the filesystem
        """

        root  = self.getCMFMountPoint()
        rlen = len(root.getPhysicalPath())

        default = lambda : ''
        portal_filter = lambda o, restricted=self.restricted, \
                        composite=self.composite_doc_types: not \
                        ( o.getId().startswith('portal_') \
                          or o.getId() in restricted \
                          or getattr(aq_base(o), 'getPortalTypeName', default)() \
                          in composite )

        fc = folder_collector()
        folders = fc(root, portal_filter)
        
        for f in folders:
            fp = f.getPhysicalPath()[rlen:]
            local = self
            
            for fps in fp:
                                    
                next = getattr(local.aq_base, fps, None)
                if next is None:
                    local.addDirectory(fps)
                local = next
                
        CMFContentStructure.inheritedAttribute('mount')(self)

    def unmount(self):
        """
        remove the container/object structure mirror of the cmf
        """
        self.manage_delObjects(self.objectIds())

    def setCompositeDocumentTypes(self, composite_types=(), _force=0, RESPONSE=None):
        """
        set content types of folderish objects which should not
        be treated as folders from a mounting pov.
        """

        pt = getToolByName(self, 'portal_types')
        all_pt = pt.objectIds()
        
        for t in composite_types:
            if not t in all_pt and not _force:
                raise InvalidPortalType("%s"%str(t))
        
        self.composite_doc_types = tuple(composite_types)

        if RESPONSE is not None:
            RESPONSE.redirect('composites_form')

    def getCompositeDocumentTypes(self):
        
        return self.composite_doc_types
    
    def setRestrictedPoints(self, restricted=(), RESPONSE=None):
        """
        set directories below the mount point that are not descendended into
        should be a set of ids
        """
        
        self.restricted = tuple([r.strip() for r in restricted if r.strip()])

        if RESPONSE is not None:
            RESPONSE.redirect('restricted_form')
        

    def setCMFMountPoint(self, cmf_mount_point, RESPONSE=None):
        """
        set a portal root relative mount point
        """

        # get rid of leading and trailing slashes
        cmf_mount = '/'.join(filter(None,cmf_mount_point.split('/')))
        self.cmf_mount_point = cmf_mount

        # make sure its valid
        try:
            self.getCMFMountPoint()
        except:
            raise InvalidCMFMountPoint("invalid mount point %s"%cmf_mount)

        if RESPONSE is not None:
            RESPONSE.redirect('cmf_mount_form')
                    
    def getCMFMountPoint(self):
        """
        get the object mount point that is the root of our structure
        """
        
        root = getToolByName(self, 'portal_url').getPortalObject()
        path = filter(None, self.cmf_mount_point.split('/'))
        for p in path:
            root = getattr(root, p)        
        return root

    def getContentPathFromDescriptor(self, descriptor):
        """
        allow for content remapping by setting content path on
        descriptor
        """
        path = descriptor.getContentPath()
        if path is not None:
            return sep.join( (self.getMountPoint(), path) )
        else:
            return self.getContentPath(descriptor.getContent())
        
    def getContentPath(self, content):
        """
        given a content object, return the object's unique filesystem
        absolute path prefix.
        """        
        # means we want the full fs path
        rlen = len(self.getCMFMountPoint().getPhysicalPath())
        return sep.join ( (self.mount_point,
                           sep.join(content.getPhysicalPath()[rlen:][:-1]) )
                          )


    def getContentRelativePath( self, content ):
        # return a path mount point relative
        rlen = len(self.getCMFMountPoint().getPhysicalPath())
        return sep.join( content.getPhysicalPath()[rlen:][:-1] )
        
        
