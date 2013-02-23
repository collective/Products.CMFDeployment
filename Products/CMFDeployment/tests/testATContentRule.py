##################################################################
#
# (C) Copyright 2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
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

import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
    
from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')

import unittest
from StringIO import StringIO
from types import StringType, NoneType
from Products.CMFCore.utils import getToolByName

from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext

from sample import registerContent, SampleImageSchemaContent, SampleImageSchemaFolder

class ATContentRuleTests( PloneTestCase ):

    def afterSetUp(self): 
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('Archetypes')                
        installer.installProduct('CMFDeployment')
     
        self.loginAsPortalOwner()

        registerContent( self.portal )
        self.portal._setObject('image_content', SampleImageSchemaContent('image_content'))
        self.image_content = self.portal.image_content         
        fh = open( os.path.join( DeploymentProductHome, 'www', 'identify.png'))
        self.portal.image_content.setPortrait( fh )
        fh.seek(0,0)
        self.raw_image = fh.read()
        fh.close()
        
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        
        self.policy = policy = deployment_tool.getPolicy('plone_example')
        self.rules = policy.getContentMastering().rules

        self.rules.manage_addProduct['CMFDeployment'].addATContentRule(
            id = "at_image_content",
            extension_expression="string:${object/getId}.html",            
            condition="python: object.portal_type == 'Sample Image Content'",
            view_method="string:base_view"
            )
        
    def beforeTearDown(self):
        self.rules = None
        self.image_content = None
        self.raw_image = None
        self.policy = None

    def testContainerRule(self):

        self.rules.manage_addProduct['CMFDeployment'].addATContainerRule(
            id = "at_container",
            extension_expression = "string:${object/getId}/index.html",
            condition = "python: object.portal_type == 'Sample Image Folder'",
            view_method = ""
            )

        self.portal._setObject( "image_folder", SampleImageSchemaFolder("image_folder") )
        image_folder = self.portal._getOb( "image_folder")
        image_folder.invokeFactory('Document', 'index_html')
        
        factory = DescriptorFactory( self.policy )
        context = getDeployExprContext( image_folder, self.portal)

        self.assertEqual(
            self.rules.at_container.isValid( image_folder, context ),
            True
            )

        descriptor = factory( image_folder )
        descriptor = self.rules.at_container.process( descriptor, context )
        
        self.assertEqual( descriptor.getRenderMethod(), "index_html")
        self.assertEqual( len(descriptor.getReverseDependencies()), 2)
        self.assertEqual( descriptor.isGhost(), True)

    def testRule(self):
        factory = DescriptorFactory( self.policy )
        descriptor = factory( self.image_content )
        context = getDeployExprContext( self.image_content, self.portal)
        
        self.assertEqual(
            self.rules.at_image_content.isValid( self.image_content, context),
            True
            )

        descriptor = self.rules.at_image_content.process( descriptor, context )
            
        self.assertEqual( len(descriptor.getDescriptors()), 2)
        return descriptor
    
    def testRendering(self):
        descriptor = self.testRule()
        mastering = self.policy.getContentMastering()
        mastering.setup()
        mastering.cook( descriptor )
        mastering.tearDown()
        descriptors = descriptor.getChildDescriptors()
        self.assertEqual( len(descriptors), 1 )
        self.assertEqual( descriptors[0].getRendered(), self.raw_image)
        return descriptor

    def XtestURIResolution(self):
        descriptor = self.testRendering()
        rendered = descriptor.getRendered()
        resolver = self.policy.getDeploymentURIs()
        self.assertEqual( 'portrait' in descriptor.getRendered(), 1 )
        resolver.addResource( descriptor )
        
        resolver.source_host = 'http://nohost'
        resolver.mount_path = '/portal'
        
        content_url = descriptor.getSourcePath() or descriptor.getContentURL()        
        marker = object()

        result = resolver.resolveURI( 'http://nohost/portal/image_content/portrait',
                                      content_url,
                                      False,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, resolver.link_error_url )
        self.assertEqual( result, '/portal/image_content/portrait.png')


    def testStorage(self):
        descriptor = self.testRendering()
        self.policy
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ATContentRuleTests))
    return suite

if __name__ == '__main__':
    framework() 
