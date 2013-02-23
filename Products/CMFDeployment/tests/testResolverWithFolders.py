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
Purpose: Unitests for testing resolution between folders and the portal root
Author: Calvin Hendryx-Parker <calvin@sixfeetup.com> @2004
License: GPL
Created: 1/2/2004
$Id: $
"""

import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')

import unittest
from types import StringType, NoneType
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.URIResolver import resolve_relative, URIResolver, test_uri_regex, test_css_regex, _marker
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext


class ResolveFolderURITests(PloneTestCase):

    def afterSetUp(self): 
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('CMFDeployment')
        self.loginAsPortalOwner()
        # add the portal site to the catalog
        catalog_tool = getToolByName(self.portal, 'portal_catalog')
        catalog_tool.indexObject(self.portal)
        self.portal.invokeFactory('Folder', 'folderwithindex')
        self.portal.invokeFactory('Folder', 'folderwithoutindex')
        self.portal.invokeFactory('Document', 'index_html')
        self.portalindex = self.portal.index_html         
        self.folderwithindex = self.portal.folderwithindex         
        self.folderwithoutindex = self.portal.folderwithoutindex         
        self.folderwithindex.invokeFactory('Document', 'index_html')         
        
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        
        self.policy = policy = deployment_tool.getPolicy('plone_example')
        self.rules = policy.getContentMastering().rules
        self.resolver = self.policy.getDeploymentURIs()
        self.resolver.source_host = 'http://www.example.com'
        self.resolver.mount_path = '/portal'
        self.resolver.target_path = '/deploy'
        
    def beforeTearDown(self):
        self.rules = None
        self.folderwithindex = None
        self.folderwithoutindex = None
        self.policy = None
        self.resolver = None

    def addResource(self, obj, type):
        factory = DescriptorFactory( self.policy )
        descriptor = factory( obj )
        context = getDeployExprContext( obj, self.portal)
        descriptor = self.rules[type].process( descriptor, context )
        mastering = self.policy.getContentMastering()
        mastering.setup()
        mastering.cook( descriptor )
        mastering.tearDown()
        rendered = descriptor.getRendered()
        self.resolver.addResource( descriptor )
        return descriptor

    def testSimpleFolderWithIndexURIResolution(self):
        folderwithindex = self.addResource(self.folderwithindex, 'Folder')
        folderwithindex_index = self.addResource(self.folderwithindex.index_html, 'IndexDocument')
        
        content_url = folderwithindex.getSourcePath() or folderwithindex.getContentURL()        
        marker = object()

        result = self.resolver.resolveURI( 'http://www.example.com/portal/folderwithindex/',
                                      content_url,
                                      True,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, self.resolver.link_error_url )
        self.assertEqual( result, '/deploy/folderwithindex/index.html')

    def testSimpleFolderWithoutIndexURIResolution(self):
        folderwithoutindex = self.addResource(self.folderwithoutindex, 'Folder')
        
        content_url = folderwithoutindex.getSourcePath() or folderwithoutindex.getContentURL()        
        marker = object()

        result = self.resolver.resolveURI( 'http://www.example.com/portal/folderwithoutindex/',
                                      content_url,
                                      True,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, self.resolver.link_error_url )
        self.assertEqual( result, '/deploy/folderwithoutindex/index.html')

    def testLinkFromFolderWithoutIndex2FolderWithIndex(self):
        folderwithoutindex = self.addResource(self.folderwithoutindex, 'Folder')
        folderwithindex = self.addResource(self.folderwithindex, 'Folder')
        folderwithindex_index = self.addResource(self.folderwithindex.index_html, 'IndexDocument')
        
        content_url = folderwithoutindex.getSourcePath() or folderwithoutindex.getContentURL()        
        marker = object()
        result = self.resolver.resolveURI( 'http://www.example.com/portal/folderwithindex/',
                                      content_url,
                                      True,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, self.resolver.link_error_url )
        self.assertEqual( result, '/deploy/folderwithindex/index.html')

    def testLinkFromFolder2Root(self):
        portalroot = self.addResource(self.portal, 'Site')
        portalroot_index = self.addResource(self.portalindex, 'IndexDocument')
        folderwithoutindex = self.addResource(self.folderwithoutindex, 'Folder')
        
        content_url = folderwithoutindex.getSourcePath() or folderwithoutindex.getContentURL()        
        marker = object()
        result = self.resolver.resolveURI( 'http://www.example.com/portal/',
                                      content_url,
                                      True,
                                      marker
                                      )

        self.assertNotEqual( result, marker )
        self.assertNotEqual( result, self.resolver.link_error_url )
        self.assertEqual( result, '/deploy/index.html')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResolveFolderURITests))
    return suite

if __name__ == '__main__':
    framework() 
