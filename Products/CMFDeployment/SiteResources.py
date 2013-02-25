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
Purpose:

    Site Resources model non portal content resources that need
    to be deployed.

    examples include things directory view css/images, but also
    can model page templates like (site_map, search_form, etc).
    
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
$Id: SiteResources.py 1245 2006-03-17 05:32:22Z hazmat $
License: GPL
"""

from Namespace import *

from DeploymentExceptions import InvalidDirectoryView
from DeploymentInterfaces import ISiteResource
        
class SiteResources(OrderedFolder):
    """
    implements merging of directory views into a deployment
    """

    meta_type = 'Content DirectoryView'

    security = ClassSecurityInfo()

    manage_options = (
        
        {'label':'Settings',
         'action':'manage_main'},

        {'label':'Policy',
         'action':'../overview'},
        
        )

    xml_key = "site_resources"
    _product_interfaces = ( ISiteResource, )

    def __init__(self, id, title=''):
        self.id = id
        self.title = title or id

    def all_meta_types(self):
        """Delegate the call passing our allowed interfaces"""
        meta_types = OrderedFolder.all_meta_types(self, interfaces=self._product_interfaces)
        filtered = []
        for t in meta_types:
            if t['action'].startswith('manage_addProduct/Products.CMFDeployment'):
                filtered.append(t)
        # filter dups
        return filtered

    security.declarePrivate('getContent')
    def getContent(self, since_time=None):
        """
        Get the content descriptors for the directory views.

        We explicitly setup descripitors with their content
        paths since we're remapping. the default content path
        is based on physical path relative to the deployment root.
        """
        if self.REQUEST.get("debug_deploy_paths"):
            raise StopIteration()
        
        for resource in self.objectValues():
            for descriptor in resource.getDescriptors( since_time ):
                yield descriptor

    security.declarePrivate('cook')
    def cook(self, descriptor):
        assert descriptor.rule_id
        rule = self._getOb( descriptor.rule_id )
        return rule.cook( descriptor )

    def getInfoForXml( self ):
        res = []
        for resource in self.objectValues():
            res.append( resource.getInfoForXml() )
        return res

InitializeClass(SiteResources)


    
    
