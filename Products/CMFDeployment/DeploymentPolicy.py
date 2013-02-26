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
$Id: DeploymentPolicy.py 1957 2007-05-14 07:26:27Z hazmat $
"""

from xml.dom.minidom import parseString
   
import DefaultConfiguration
import Log
import pipeline
import io

from Namespace import *
from DeploymentInterfaces import IDeploymentPolicy
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class DeploymentPolicy(Folder):

    meta_type = 'Deployment Policy'

    implements(IDeploymentPolicy)

    security = ClassSecurityInfo()
    security.declareObjectProtected(CMFCorePermissions.ManagePortal)

    manage_options = (

        {'label':'Overview',
         'action':'overview'},
        
        {'label':'Identification',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentIdentification},

        {'label':'Organization',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentOrganization},

        {'label':'Resources',
         'action':'%s/manage_workspace'%DefaultConfiguration.SiteResources},

        {'label':'URIs',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentURIs},

        {'label':'Rendering',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentMastering},

        {'label':'Transports', 
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentDeployment},

        {'label':'Transforms',
         'action':'%s/manage_workspace'%DefaultConfiguration.ContentTransforms},
        
        {'label':'History',
         'action':'%s/manage_workspace'%DefaultConfiguration.DeploymentHistory},
        
        ) 

    overview = DTMLFile('ui/PolicyOverview', globals())
    debug_policy = DTMLFile('ui/PolicyDebug', globals())
    identification = DTMLFile('ui/ContentIdentification', globals())
    preview = DTMLFile('ui/PolicyPreview', globals())
    _active = 1
    _reset_date = False
    policy_xml = DTMLFile('ui/PolicyExport', globals())
    xml_key = 'policy'

    icon = 'misc_/CMFDeployment/policy.png'
    
    def __init__(self, id, title, pipeline_id):
        self.id = id
        self.title = title
        self.pipeline_id = pipeline_id

        assert pipeline_id in pipeline.getPipelineNames(), "invalid pipeline"

    def getContentIdentification(self):
        return self._getOb(DefaultConfiguration.ContentIdentification)

    def getContentOrganization(self):
        return self._getOb(DefaultConfiguration.ContentOrganization)

    def getContentMastering(self):
        return self._getOb(DefaultConfiguration.ContentMastering)

    def getContentDeployment(self):
        return self._getOb(DefaultConfiguration.ContentDeployment)

    def getContentTransforms(self):
        return self._getOb(DefaultConfiguration.ContentTransforms)

    def getContentSources( self ):
        return self.getContentIdentification().sources

    def getDeploymentTransports( self ):
        return self._getOb(DefaultConfiguration.ContentDeployment)

    def getSiteResources( self ):
        return self._getOb(DefaultConfiguration.SiteResources)

    def getContentRules( self ):
        return self.getContentMastering().rules
    
    def getDeploymentHistory(self):
        return self._getOb(DefaultConfiguration.DeploymentHistory)

    def getDeploymentURIs(self):
        return self._getOb(DefaultConfiguration.ContentURIs)

    def getDeploymentPolicy(self):
        return self

    security.declareProtected('Manage Portal', 'clearState')
    def clearState(self, RESPONSE=None):
        """
        clear all persistent state from the policy, not including
        configuration.
        """
        self.getDeploymentHistory().clear()
        self.getDeploymentURIs().clear()

        factory = pipeline.getPipeline( self.pipeline_id )
        factory.clearState( self )
        
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declarePrivate('getPipeline')
    def getPipeline(self):
        factory = pipeline.getPipeline( self.pipeline_id )
        deployment_pipeline = factory()
        return deployment_pipeline

    def setActive(self, flag, RESPONSE=None):
        self._active = not not flag
        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def isActive(self):
        return self._active
    
    def setResetDate(self, flag):
        """ Set the state of the reset flag
        """
        self._reset_date = flag

    def getResetDate(self):
        """ Returns true if the incremental date should be ignored in the next deploy
        """
        return self._reset_date

    security.declareProtected('Manage Portal', 'previewDeployment')
    def previewDeployment( self ):
        preview_factory = pipeline.PreviewPipelineFactory()
        preview = preview_factory()
        preview.process( self )
        return {'descriptors':preview.variables.get('descriptors'),
                'deletions':preview.variables.get('deletions') }
    
    def execute(self, REQUEST=None, RESPONSE=None):
        """ """
        if not self.isActive():
            return
        
        if getattr(REQUEST, 'reset_date', False):
            self.setResetDate(True)

        histories = self.getDeploymentHistory()
        history = histories.makeHistory()
    
        Log.attachLogMonitor(history)
        
        try:
            try:
                pipeline = self.getPipeline()
                pipeline.process( self )
            except:
                if not DefaultConfiguration.DEPLOYMENT_DEBUG:
                    raise
                import sys, pdb, traceback
                ec, e, tb = sys.exc_info()
                print ec, e
                print traceback.print_tb( tb )
                #pdb.post_mortem( tb )
                raise 
        finally:
            Log.detachLogMonitor(history)

        #history.recordStatistics(display)
        histories.attachHistory(history)

        self.getDeploymentPolicy().setResetDate(False)
        #Uncomment if/when you want to have users with Manager role receive email
        #when a deployment completes. Helpful, for large sites with long-running
        #deployments.
        #self.exportNotify(REQUEST)
        
        if RESPONSE:
            return RESPONSE.redirect('manage_workspace')
        return True

    def exportNotify(self, REQUEST):
        plone_utils = self.aq_parent.plone_utils
        mailhost=None
        pm=None
	try:
    	   pm = self.aq_parent.portal_membership
	except:
    	    raise AttributeError, "Can't find pm tool"

	zopeusers = []

	for user in pm.listMembers():
	    localroles = pm.getMemberById(user.id).getRolesInContext(self.aq_parent.aq_parent);

	    if 'Manager' in localroles:
               zopeusers.append(user.getProperty('email') )

	mTo = ','.join(zopeusers)

        try:
           mailhost=self.aq_parent.MailHost
        except:
           raise AttributeError, "Can't find a Mail Host object"

        encoding=self.aq_parent.email_charset
        obj_url=self.aq_parent.preview_domain.replace('-preview','-static')
        sys_name=obj_url.replace('-static','')
        mMsg = "The export has completed. To review the results browse to: %s \n\n\n\n---\nCMS Portal Administrator" % (obj_url)
        mFrom = self.aq_parent.email_from_address
        mSubj = "Export has completed on %s" % (sys_name)

#Enable to notify site Managers by email that deployment is done
        try:
           mailhost.send(mMsg, mTo, mFrom, subject=mSubj)
        except:
           pass # do not fail if email is not sent


    def manage_afterAdd(self, item, container):
        DefaultConfiguration.install(self)

        factory = pipeline.getPipeline( self.pipeline_id )
        try:
            factory.finishPolicyConstruction( self )
        except:
            if not DefaultConfiguration.DEPLOYMENT_DEBUG:
                raise
            import traceback, sys, pdb
            traceback.print_exc()
            pdb.post_mortem(sys.exc_info()[-1])

    def manage_beforeDelete(self, *args):
        factory = pipeline.getPipeline( self.pipeline_id )
        factory.beginPolicyRemoval( self )
        
    def export( self, compact=False, RESPONSE=None ):
        """
        export to xml for download
        """
        ctx = io.ExportContext()
        ctx.load( self )
        try:
            export = ctx.construct()
        except:
            import pdb, traceback, sys
            exc_info = sys.exc_info()
            traceback.print_exception( *exc_info )
            #pdb.post_mortem( exc_info[-1] )
            raise

        if not compact:
            dom = parseString( export )
            export = dom.toprettyxml()

        if RESPONSE is not None:
            RESPONSE.setHeader("Content-Type", 'text/xml')
            RESPONSE.setHeader("Content-Length", len( export ) )
            RESPONSE.setHeader("Content-Disposition",
                               'attachment; filename="%s.xml"'%(self.getId()))

        return export
    
    def getInfoForXml( self ):
        info =  {'attributes':{'id':self.id,
                               'title': self.title_or_id(),
                               'pipeline_id': self.pipeline_id } }
        for ob in self.objectValues():
            if hasattr( aq_base( ob ), 'xml_key' ):
                info[ob.xml_key] = ob.getInfoForXml()
        return info
    
InitializeClass(DeploymentPolicy)
    

