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
Purpose: Unitests for Site Export

***
These tests now require installation of example ATContentRule Product
and Archetypes.
***

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 12/29/2002
$Id: $

"""

import os, sys, time, shutil, commands
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Testing import ZopeTestCase

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('kupu')

from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

import unittest
from StringIO import StringIO
from types import StringType, NoneType
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import DeploymentProductHome

from sample import SampleImageSchemaContent, registerContent

TESTDEPLOYDIR = os.path.join( DeploymentProductHome, 'tests', 'deploy')

# these too settings operate together
LEAVE_DEPLOY_DIR=True
CLEAN_DEPLOY_DIR=True

def setupContentTree( portal ):

    portal.portal_catalog.indexObject( portal )

    # Try to remove news if it existed, like in plone 2.1
    try:
        portal.manage_delObjects(["news"])
    except:
        pass

    portal.invokeFactory('Folder', 'news')
    portal.news.invokeFactory('Document','index_html')
    
    news_index_content = '''\
    <html>
    <body>
    # relative url
    <a href="../about">About Us</a>

    # absolute url
    <a href="/portal/about/contact">Jobs - You Wish!</a>    

    # javascript url
    <a href="javascript:this.print()">Print Me</a>    

    # mailto url
    <a href="mailto:deployment@example.com">Print Me</a>    
    
    # test self referencing content
    <a href="./index_html"> My Self </a>
    <a href="/portal/news">My Self aliased</a>
    <a href=".">My Self</a>
    
    # test anchor link inside of page
    <a href="#furtherdown">Down the page</a>
    
    this is some more text
    
    <a name="furtherdown"></a>
    here is stuff that is further down the page.
    </body>
    </html>
    '''
    
    portal.news.index_html.edit(text_format='html', text=news_index_content)
    portal.invokeFactory('Folder', 'about')
    
    
    portal.about.invokeFactory( 'Document', 'index_html')
    about_index_content = '''
    <html><body>
    Case Studies
    
    case studies... <a href="/portal/logo.jpg"> Logo </a>
    we eaten at millions of mcdonalds...

    Dig our Cool JavaScript 
    <javascript src="/portal/plone_javascripts.js"/>
    <img src="/portal/vera.jpg"> logo </src>
    <img src="../vera.jpg"> logo </src>    
    </body>
    </html>
    '''
    
    portal.about.index_html.edit(text_format="html", text=about_index_content)
    portal.about.invokeFactory('Document', 'contact')
    
    # Try to remove events if it existed, like in plone 2.1
    try:
        portal.manage_delObjects(["events"])
    except:
        pass
        
    portal.invokeFactory('Folder','events')
    portal.events.invokeFactory( 'Event', 'Snow Sprint')
    portal.events['Snow Sprint'].edit( 
        title='Snow Sprint',
        description="fun not in the sun",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="http://darpa.gov")
        
    portal.events.invokeFactory('Event', 'cignex_sprint')
    portal.events.cignex_sprint.edit(
        title='Cignex Sprint',
        description="fun in the fog",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="http://hazmat.gov")    
        
    logo = portal['logo.jpg']
    image_content = str(logo)
    portal.invokeFactory('Image', 'vera.jpg')
    #portal['vera.jpg'].edit(file=image_content)

    #content = SampleImageSchemaContent('image_test')
    #portal.events._setObject( content.id, content )
    #portal.events['image_test'].setPortrait( image_content )        
    #fh.close()
    
class DeploymentTests( PloneTestCase ):

    def afterSetUp(self): 
        self.loginAsPortalOwner()

        if os.path.exists( TESTDEPLOYDIR ) and CLEAN_DEPLOY_DIR:
            shutil.rmtree( TESTDEPLOYDIR )
        
        if not os.path.exists( TESTDEPLOYDIR ):
            os.mkdir( TESTDEPLOYDIR )

        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('Archetypes')
        installer.installProduct('CMFDeployment')

        #registerContent( self.portal )
        setupContentTree(self.portal)
        
        policy_file = os.path.join( DeploymentProductHome, 'examples', 'policies', 'plone.xml') 
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        policy = deployment_tool.getPolicy('plone_example')
        structure = policy.getContentOrganization().getActiveStructure()
        structure.mount_point = TESTDEPLOYDIR
        fh.close()
        get_transaction().commit(1)
        self.portal.changeSkin( self.portal.portal_skins.getDefaultSkin() )

        rules = policy.getContentMastering().rules
        rules.manage_addProduct['CMFDeployment'].addATContentRule(
            id = "at_image_content",
            extension_expression="string:${object/getId}.html",
            condition="python: object.portal_type == 'Sample Image Content'",
            view_method="string:base_view",
            )
        
        
    def beforeTearDown(self):
        if os.path.exists( TESTDEPLOYDIR ) and not LEAVE_DEPLOY_DIR:
            shutil.rmtree( TESTDEPLOYDIR )

    def testDeploy(self):
        # push the content to the fs
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        try:
            deployment_tool.plone_example.execute()
        except:
            import pdb, sys
            ec, e, tb = sys.exc_info()
            print ec, e
            pdb.post_mortem(tb)

        command = "grep -rl deploy_link_error %s/*"%TESTDEPLOYDIR
        
        status, output = commands.getstatusoutput(
            command
            )
            
        if status and output:
            raise AssertionError, "Could not verify content \n %s \n %s \n%s"%(command, status, output)
            
        lines = filter(None, output.strip().split('\n'))
        if not lines:
            return

        print "Files with Link Errors"
        for line in lines:
            print " ", line


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DeploymentTests))
    return suite

if __name__ == '__main__':
    framework() 
