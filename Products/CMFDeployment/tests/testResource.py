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
$Id: testResource.py 1660 2006-09-14 02:34:15Z hazmat $

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

class SiteResourceTests( PloneTestCase ):

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
        
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone21.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_id="test21", policy_xml=fh )
        fh.close()
        
        self.policy = policy = deployment_tool.getPolicy('test21')
        self.resources = policy.getSiteResources()
        
##         self.rules = policy.getContentMastering().rules
##         self.rules.manage_addProduct['CMFDeployment'].addATContentRule(
##             id = "at_image_content",
##             extension_expression="string:${object/getId}.html",            
##             condition="python: object.portal_type == 'Sample Image Content'",
##             view_method="string:base_view"
##             )
        
    def beforeTearDown(self):
        self.resources = None
        self.image_content = None
        self.raw_image = None
        self.policy = None

    def testAuthorIndexRule(self):
        self.resources.manage_addProduct['CMFDeployment'].addAuthorIndexesRule(
            id = "authors_index",
            source_path = "/author/",
            view_path = "/author/",
            deployment_path = "/authors/"
            )

        self.portal._setObject( "image_folder", SampleImageSchemaFolder("image_folder") )
        image_folder = self.portal._getOb( "image_folder")
        image_folder.invokeFactory('Document', 'index_html')

        descriptors = list(self.resources.authors_index.getDescriptors())
        self.assertEqual( len(descriptors), 1 )

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SiteResourceTests))
    return suite

if __name__ == '__main__':
    framework() 
