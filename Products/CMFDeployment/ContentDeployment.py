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
Purpose: Defines Mechanisms and Data needed
         to transport content from zope server
         fs to deployment target(s).

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: ContentDeployment.py 1245 2006-03-17 05:32:22Z hazmat $
"""

from Namespace import *
from DeploymentInterfaces import *
from DeploymentExceptions import *
from utils import getXmlPath

#################################
# container for pluggable transports

class ContentDeployment( OrderedFolder ):

    meta_type = 'Content Deployment'

    manage_options = (

        {'label':'Targets',
         'action':'manage_main'},

        {'label':'Overview',
         'action':'overview'},
        
        ) + App.Undo.UndoSupport.manage_options

    overview = DTMLFile('ui/ContentDeploymentOverview', globals())

    xml_key = 'transports'
    _product_interfaces = ( IDeploymentTarget, )

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    def all_meta_types(self):
        """Delegate the call passing our allowed interfaces"""
        return OrderedFolder.all_meta_types(self, interfaces=self._product_interfaces)

    security.declarePrivate('deploy')
    def deploy(self, structure):
        for target in self.objectValues():
            target.transfer( structure )

    def getInfoForXml( self ):
        res = []
        for transport in self.objectValues():
            res.append( transport.getInfoForXml() )
        return res


InitializeClass( ContentDeployment )

