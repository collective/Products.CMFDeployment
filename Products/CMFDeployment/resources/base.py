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
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: base.py 1245 2006-03-17 05:32:22Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import ISiteResource
from Products.CMFDeployment.utils import SerializablePlugin

source_template = """\
 <resource id="%(id)s"
           product="%(product)s"
           factory="%(factory)s"
           view_path="%(view_path)s"
           deployment_path="%(deployment_path)s"
           source_path="%(source_path)s"
           />
"""         

class SiteBaseResource( SerializablePlugin ):

    __implements__ = ISiteResource

    meta_type = "Site Resource"
    xml_template = source_template
    xml_factory  = ""

    security = ClassSecurityInfo()

    manage_options = (
        
        {'label':'Settings',
         'action':'manage_settings'},
        
        )
    security.declareProtected(CMFCorePermissions.ManagePortal, ('manage_settings') )
    manage_settings = DTMLFile('../ui/ResourceGenericEditForm', globals())

    def __init__(self, id, view_path, source_path, deployment_path):
        self.id = id
        self.view_path = view_path.strip()
        self.source_path = source_path.strip()
        self.deployment_path = deployment_path.strip()
        self.setTitle()

    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self, view_path, source_path, deployment_path, RESPONSE=None):
        """
        edit a resource
        """
        self.view_path = view_path.strip()
        self.source_path = source_path.strip()
        self.deployment_path = deployment_path.strip()
        self.setTitle()

        if not self.isValid( self.aq_inner.aq_parent ):
            raise InvalidResource("% is not valid"%str(view_path))

        if RESPONSE is not None:
            container = self.getParentNode()
            return RESPONSE.redirect("%s/manage_main"%container.absolute_url())

    def conflicts(self, container ):
        return False

    def isValid(self, container):
        return True

    def getInfoForXml(self):
        d = SerializablePlugin.getInfoForXml(self)
        del d['attributes']['title']
        d['view_path'] = self.view_path
        d['deployment_path'] = self.deployment_path
        d['source_path'] = self.source_path
        return d

    def setTitle(self):
        self.title = "%s -> %s -> %s"%(self.view_path,
                                       self.source_path,
                                       self.deployment_path)
    
InitializeClass( SiteBaseResource )
