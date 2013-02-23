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
$Id: registry.py 1204 2006-03-04 10:18:50Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from base import SiteBaseResource
from Products.CMFDeployment.Log import LogFactory
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.URIResolver import clstrip, extend_relative_path

from Products.CMFDeployment.DeploymentExceptions import InvalidDirectoryView

log = LogFactory('Resource Registries')

#KW: from Interface import Interface, Attribute
from zope.interface import Interface

addResourceRegistryRuleForm = DTMLFile('../ui/ResourceRegistryAddForm', globals())

def addResourceRegistryRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
    """
    add a registry to the listing of deployable registries, after
    verifying the the view_path. 

    view_path - dv path relative to portal_skin
    deployment_path - path to deploy to relative to d. root
    source_path - the path that directory view appears relative to mount root,
       when doing uri resolution.
    """

    # XXX is this really nesc, i think not the functionality is self
    # contained to this module, we should allow deployments of the
    # view path multiple times, also needs mod in policy export.dtml
    view_path = view_path.strip()

    rule = ResourceRegistryRule( id,
                                 view_path,
                                 source_path,
                                 deployment_path )

    container = self.this()
    if rule.conflicts( container ):
        raise InvalidRegistry("View Path already exists")

    if not rule.isValid( container ):
        raise InvalidRegistry("%s is not valid"%str(view_path))

    self._setObject( id, rule )

    if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')
            

class ResourceRegistryRule( SiteBaseResource ):

    meta_type = "Resource Registry Rule"
    security = ClassSecurityInfo()

    xml_factory = "addResourceRegistryRule"
    icon = 'misc_/CMFDeployment/resource_registry.gif'

    security.declarePrivate('getRegistry')
    def getRegistry(self, path):
        """
        returns the registry given by the portal root
        relative 'path'
        """
        
        root = getToolByName(self, 'portal_url').getPortalObject()
        components = filter(None, path.split('/'))

        d = root
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                raise InvalidRegistry(
                    "registry does not exist %s of %s"%(c, path)
                    )
            
        return d
    
    security.declarePrivate('getDescriptors')
    def getDescriptors(self, since_time=None):
        """
        Get the content descriptors for the registry.

        We explicitly setup descripitors with their content
        paths since we're remapping. the default content path
        is based on physical path relative to the deployment root.

        since_time ignored
        """
        res = []

        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())

        r = self.getRegistry( self.view_path )
        content = r.getEvaluatedResources(self)
        source_path, deploy_path = self.source_path, self.deployment_path 

        uris = self.getDeploymentPolicy().getDeploymentURIs()
        vhost_path = uris.vhost_path

        # get rid of trailing and leading slashes and join to base path
        source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))
        deploy_path = '/'.join(filter(None, deploy_path.split('/')))

        # XXX the escaping seems weak.. - use a std lib func, and allow for multiple source paths.
        skin_name = self.getCurrentSkinName().replace(' ', '%20')

        for c in content:
            inline = getattr(c, "getInline", None) and c.getInline() or False
            if inline:
                continue
            d = ContentDescriptor(c)
            c.registry = r
            d.setContentPath(deploy_path)
            d.setFileName(c.getId())

            v = "%s/%s/%s"%(source_path, skin_name, c.getId())
            d.setSourcePath('/'.join(filter(None,v.split('/'))))
            d.setRenderMethod('')
            d.rule_id = self.getId()
            res.append(d)
                
        return res


    security.declarePrivate('cook')
    def cook(self, descriptor ):
        obj = descriptor.getContent()
        registry = obj.registry.__of__(self)
        #import pdb; pdb.set_trace();

        try:
           rendered, content_type = registry[ obj.getId() ]
           descriptor.setRendered( rendered )        
        except:
           log.warning("Problem cooking resource with id: %s" % (obj.getId()) )
    
