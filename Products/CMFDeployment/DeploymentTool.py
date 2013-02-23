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
Purpose: das deployment tool
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: DeploymentTool.py 1657 2006-09-13 22:00:32Z hazmat $
"""


from Namespace import *
from DeploymentPolicy import DeploymentPolicy
from reader import read_policy, make_policy
import io

class DeploymentTool(UniqueObject, Folder):

    id = 'portal_deployment'

    title = "Controls how content can be deployed to external systems"
    meta_type = 'Deployment Tool'
    
    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.ManagePortal)

    manage_options = (

        {'label':'Policies',
         'action':'manage_main'},
        
        {'label':'Overview',
         'action':'overview'},

        )

    overview = DTMLFile('ui/ToolOverview', globals())
    addPolicyForm = DTMLFile('ui/ToolAddPolicyForm', globals())

    all_meta_types = (
        {'name':DeploymentPolicy.meta_type,
         'action':'addPolicyForm'},
        )

    security.declareProtected(CMFCorePermissions.ManagePortal, 'addPolicy')
    def addPolicy(self, policy_id='', policy_title='', policy_pipeline_id='incremental', policy_xml='', REQUEST=None):
        """  """

        if not policy_xml:
            policy = DeploymentPolicy(policy_id, policy_title, policy_pipeline_id)
            self._setObject(policy_id, policy )
            
            policy = self._getOb(policy_id)
            
            if REQUEST is not None:
                return REQUEST.RESPONSE.redirect(policy.absolute_url()+'/manage_workspace')
            return policy
        
        # import from xml
        overrides = {}
        overrides['id'] = policy_id
        overrides['title'] = policy_title

        ctx = io.ImportContext( self, overrides )
        ctx.load( policy_xml )

        policy = ctx.construct()            
        
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(policy.absolute_url()+'/manage_workspace')

        return policy

    security.declareProtected(CMFCorePermissions.ManagePortal, 'removePolicy')        
    def removePolicy(self, policy_id):
        self._delObject(policy_id)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getPolicy')
    def getPolicy(self, policy_id):
        return self._getOb(policy_id)



