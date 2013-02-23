##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net
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
resource templates model a context  template which 

$Id: template.py 1253 2006-03-20 08:55:11Z hazmat $
"""


from Products.CMFDeployment.Namespace import *
from base import SiteBaseResource
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.URIResolver import clstrip, extend_relative_path

from directoryview import cook

addResourceTemplateRuleForm = DTMLFile('../ui/ResourceTemplateAddForm', globals())

def addResourceTemplateRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
    """
    add a resource template
    """
    view_path = view_path.strip()
    rule = ResourceTemplateRule( id,
                                 view_path,
                                 source_path,
                                 deployment_path )    
    self._setObject( id, rule )

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')


class ResourceTemplateRule( SiteBaseResource ):

    meta_type = "Template Resource Rule"
    security = ClassSecurityInfo()

    icon = 'misc_/PageTemplates/zpt.gif'
    xml_factory = "addResourceTemplateRule"

    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self, view_path, source_path, deployment_path, RESPONSE=None):
        """
        edit template rule
        """
        SiteBaseResource.edit( self, view_path, source_path, deployment_path)
        
        # assert valid data
        descriptors = self.getDescriptors()

        if RESPONSE is not None:
            container = self.getParentNode()
            return RESPONSE.redirect("%s/manage_main"%container.absolute_url())
        
    def getDescriptors(self, since_time=None):
        """
        return the descriptor corresponding to this template resource
        
        since_time ignored
        """

        portal = self.portal_url.getPortalObject()
        view_path = self.view_path
        if view_path.startswith('/'):
            view_path = view_path[1:]
        
        ob = portal.restrictedTraverse( view_path )

        source_path, deploy_path = self.source_path, self.deployment_path 
        uris = self.getDeploymentPolicy().getDeploymentURIs()
        vhost_path = uris.vhost_path

        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())
            
        # get rid of trailing and leading slashes and join to base path
        source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))

        assert '/' in deploy_path

        idx = deploy_path.rfind('/')
        content_path = deploy_path[:idx]
        file_name = deploy_path[idx+1:]
            
        content_path = '/'.join(filter(None, content_path.split('/')))

        d = ContentDescriptor( ob )
        d.setContentPath(content_path)
        d.setFileName( file_name )
        d.setSourcePath( source_path )
        d.setRenderMethod('')        
        d.rule_id = self.getId()

        return [d]

    def cook(self, descriptor):
        return cook( self, descriptor )
