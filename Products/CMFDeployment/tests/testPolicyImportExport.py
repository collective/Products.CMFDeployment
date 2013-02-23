##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: Unitests for Polixy Xml Import Export
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 12/29/2002
$Id: $

"""

import os, sys, time, StringIO
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
    
from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')

import unittest
from StringIO import StringIO
from types import StringType, NoneType
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment import io

class PolicyImportExportTests( PloneTestCase ):

    def afterSetUp(self): 
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('CMFDeployment')
        
    def beforeTearDown(self):
        pass

    def testImport(self):
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml') 
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        # do some sanity checks
        assert 'plone_example' in deployment_tool.objectIds()
   
    def testExport(self):
        """
        Running the export of the policy
        """
        # Viewing the policy requires manage portal permission
        self.loginAsPortalOwner()
        self.testImport()
        dtool = getToolByName(self.portal, 'portal_deployment')
        xml = dtool.plone_example.policy_xml()     
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml') 
        fh = open(policy_file)
        fs = fh.read()
        fh.close()
        return fs
        
    def testIOCycle(self):
        xml = StringIO( self.testExport() )
        dtool = getToolByName(self.portal, 'portal_deployment')
        dtool.manage_delObjects(['plone_example'])
        dtool.addPolicy( policy_xml = xml )
        self.assertEqual(
            dtool.getPolicy('plone_example').getContentMastering().rules.Folder.condition_text,
            "python: object.portal_type == 'Folder'"
            )

    def testTransportIssue1( self ):
        policy_file = os.path.join( DeploymentProductHome, 'tests', 'io_data.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        policy = deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.assertTrue( 'vx' in policy.getContentDeployment().objectIds() )
        
    def testBooleanIssue4 (self ):
        policy_file = os.path.join( DeploymentProductHome, 'tests', 'io_data.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        policy = deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.assertFalse( policy.getDeploymentURIs().relative_target_resolution )

    def testInfoForXml(self):
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml') 
        fh = open( policy_file )
        
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
            
        example = deployment_tool._getOb( 'plone_example')
        info = example.getInfoForXml()
        #import pprint
        #pprint.pprint( info )

    def testXmlGeneration(self):
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone21.xml') 
        fh = open( policy_file )
        
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        example = deployment_tool._getOb( 'incremental')
        self.assertEqual( len(example.getContentMastering().rules.Event.objectIds()), 2)
        export = example.export()
        return export

    def xtestXmlParsing(self):

        xstr = self.testXmlGeneration()
        ctx  = io.ImportContext( None, {} )
        stream = StringIO( xstr )

        try:
            ctx.load( stream )
        except:
            import pdb, traceback, sys
            exc_info = sys.exc_info()
            traceback.print_exception( *exc_info )
            pdb.post_mortem( exc_info[-1] )

        return ctx

    def xestXmlImport( self ):
        ctx = self.testXmlParsing()

        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        example = deployment_tool._getOb( 'plone21_example')        
        ctx.context = example
        ctx.overrides = {'id':'test_xio'}
        try:
            ctx.construct()
        except:
            import pdb, traceback, sys
            exc_info = sys.exc_info()
            traceback.print_exception( *exc_info )
            pdb.post_mortem( exc_info[-1] )

        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PolicyImportExportTests))
    return suite

if __name__ == '__main__':
    framework() 
