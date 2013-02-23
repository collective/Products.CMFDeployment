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
Purpose: Renders Content For Deployment
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: ContentMastering.py 1952 2007-05-10 03:23:50Z hazmat $
"""

import types
import urllib, tempfile

from Namespace import *

import DefaultConfiguration

from ContentRules import ContentRuleContainer
from DeploymentExceptions import InvalidSkinName
from Descriptor import DescriptorFactory
from ExpressionContainer import getDeployExprContext

from zope.annotation import IAnnotations
from plone.memoize.view import ViewMemo

from utils import file2string, is_baseunit

from Log import LogFactory

log = LogFactory('Mastering')

class ContentMastering(Folder):

    meta_type = 'Content Mastering' 

    manage_options = (

        {'label':'Rules',
         'action':'rules/manage_main'},        
        
        {'label':'Skin',
         'action':'skin'},

        {'label':'User',
         'action':'user'},

        {'label':'Overview',
         'action':'overview'},

        {'label':'Policy',
         'action':'../overview'}

        )

    security = ClassSecurityInfo()
    
    overview = DTMLFile('ui/ContentMasteringOverview', globals())
    skin     = DTMLFile('ui/ContentMasteringSkin', globals())
    root     = DTMLFile('ui/ContentMasteringRoot', globals())
    user     = DTMLFile('ui/ContentMasteringUser', globals())

    xml_key = 'mastering'


    
    def __init__(self, id):
        
        self.id = id
        self.skn_name = None

    security.declareProtected('Manage portal', 'editRoot')
    def editRoot(self, enable, server, server_path, port, protocol, RESPONSE=None):
        """ """
        
        self.site_root.edit(enable, server, server_path, protocol, port)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    security.declareProtected('Manage portal', 'editSkin')
    def editSkin(self, enable, skin_name, RESPONSE=None):
        """ """
        
        skin_tool = getToolByName(self, 'portal_skins')
        skin = skin_tool.getSkinByName(skin_name.strip())
        
        if skin is None:
            raise InvalidSkinName("%s is not a valid skin"%str(skin_name))

        self.site_skin.edit(enable, skin_name)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    security.declareProtected('Manage portal', 'editUser')
    def editUser(self, enable, user, udb_path, RESPONSE=None):
        """ """

        self.site_user.edit(enable, user, udb_path)

        if RESPONSE is not None:
            RESPONSE.redirect('overview')

    def manage_afterAdd(self, item, container):

        if self._getOb('rules', None) is None:
            ob = ContentRuleContainer('rules')
            self._setObject('rules', ob)

        if self._getOb('site_user', None) is None:
            ob = SiteChainUser()
            self._setObject('site_user', ob)

        if self._getOb('site_skin', None) is None:
            ob = SiteChainSkin()
            self._setObject('site_skin', ob)

    #################################

    security.declarePrivate('prepareContent')
    def prepareContent(self, content):
        """
        attempt to prepare a content object, for testing purposes
        """

        factory = DescriptorFactory( self )
        descriptor = factory( content )
        self.prepare( descriptor )

        return descriptor.rule_id or "Not Deployed"

    security.declarePrivate('prepare')        
    def prepare(self, descriptor):
        """
        prepare a descriptor for deployment by finding and applying a
        deployment/content/mime rule for it.
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        c = descriptor.getContent()
        ctx = getDeployExprContext(c, portal) 
        mappings = self.rules.objectValues()
        for m in mappings:
            if m.isValid( c, ctx):
                m.process( descriptor, ctx )
                return True
        log.debug('no rule for (%s)->(%s)'%(str(c.portal_type), descriptor.content_url))
        return None

    security.declarePrivate('cook')        
    def cook(self, descriptor):
        """
        render the contents of a descriptor and its child descriptors
        """

        if descriptor.isGhost():
            return

        # get child descriptors if any
        descriptors = descriptor.getDescriptors()

        # sometimes the skindata can disappear mid request
        # xxx we now modify the portal root at the start to prevent
        # volatile disappearance, so this should be unesc.

        # Ok, on Plone 2.1, _v_skindata doesn't exist...  So, we try
        # to use getCurrentSkinName if available, and fallback to
        # _v_skindata else
        #root = self.portal_url.getPortalObject()
        #skin = getattr(root, "getCurrentSkinName", None)
        #if skin:
        #    skin = skin()
        #else:
        #    skin = root._v_skindata
        #if not skin:
        #    self.site_skin._setSkin()

        self.renderContentUrl(descriptor)
        
        for child_descriptor in descriptor.getChildDescriptors():
            self.renderContent(child_descriptor)

    def renderContentUrl(self, descriptor):
        """
        Render a content via url retrieval.
        """
        c = descriptor.getContent()
        url = c.absolute_url()

        fh = urllib.urlopen(url)
        try:
            rendered = fh.read()
        except:
            descriptor.setGhost(1)
        else:
            descriptor.setRendered(rendered)
        
    security.declarePrivate('renderContent')
    def renderContent( self, descriptor ):

        c = descriptor.getContent()
        vm = descriptor.getRenderMethod()

        if vm is None: # XXX redundant
            descriptor.setGhost(1)
            return

        # Clear out request annotations between renderings
        request_annotations = IAnnotations(self.REQUEST)
        if ViewMemo.key in request_annotations:
            del IAnnotations(self.REQUEST)[ViewMemo.key]
    
        if callable( vm ):
            render = vm
        else:
            render = getattr(c, vm, None) or getattr(c, '__call__', None)
                                                 
        if render is None:
            try:
                log.error(" couldn't find render method for %s %s"%( str(descriptor.content_url), str(c.getPortalTypeName()) ))
            except Exception, e:
                print e
                      
        # this is just a tad verbose..
        #log.debug('rendering %s %s %s'%(c.getId(), vm, repr(render)))

        try:
            if getattr(aq_base(render), 'isDocTemp', 0):
                rendered = apply(render, (self, self.REQUEST) )

            # check if the view method returned a file like object for a renderer
            elif hasattr( aq_base( render ), 'precondition'):
                rendered = file2string( render )
                descriptor.setBinary(1)
                
            # test if the content is a file object, but not an AT BaseUnit              
            elif hasattr(aq_base(c), 'precondition') and  not is_baseunit(c):
                rendered = file2string( c )
                descriptor.setBinary(1)
            else:
                rendered = render()
                
            # if a render method returns a file
            if hasattr( aq_base( rendered ), 'precondition') and not is_baseunit(c):
                rendered = file2string( rendered )
                descriptor.setBinary(1)
                
            # sanity check the output
            if not isinstance( rendered, (str, unicode) ):
                log.error("invalid rendering output for %s %s %s %s"%( descriptor.content_url, repr( vm ), repr( render ) ) )
                descriptor.setGhost(1)
                return
            
            descriptor.setRendered( rendered )

        except:
            if False and DefaultConfiguration.DEPLOYMENT_DEBUG:
                import sys, pdb, traceback
                ec, e, tb = sys.exc_info()
                print ec, e
                traceback.print_tb( tb )
                pdb.post_mortem( tb )
                raise

            import traceback
            traceback.print_exc()
            log.error('Error While Rendering %s'%( '/'.join(c.getPhysicalPath()) ) )
            descriptor.setGhost(1) # ghostify it        
            #raise
            
    #################################
    def setup(self):
        #self.site_root.lock()
        self.site_skin.lock()
        self.site_user.lock()
        
    def tearDown(self):
        #self.site_root.unlock()
        self.site_skin.unlock()
        self.site_user.unlock()

    #################################
    security.declarePrivate('getInfoForXml')
    def getInfoForXml( self ):
        d = { 'chain_skin' : self.site_skin.getInfoForXml(),
              'chain_user' : self.site_user.getInfoForXml() }
        d['rules'] = self.rules.getInfoForXml()['rules']
        return d

    security.declarePrivate('getFromStruct')
    def fromStruct( self, struct ):
        self.site_skin.edit( struct.chain_skin.enable,
                             struct.chain_skin.attributes.skin_name )
        
        self.site_user.edit( struct.chain_user.enable,
                             struct.chain_user.attributes.user,
                             struct.chain_user.attributes.udb_path )

class SiteChainSkin(SimpleItem):
    """

    changes the skin mid request,

    """

    meta_type = 'Site Chain Skin'
    id = 'site_skin'
    
    _v_active = None
    _v_saved_skin_name = None

    enable = 1    
    security = ClassSecurityInfo()
    
    def __init__(self):
        self.skin_name = None 

    security.declareProtected('Manage portal', 'edit')
    def edit(self, enable, skin_name):
        
        self.enable = not not int(enable)
        self.skin_name = skin_name

    security.declarePrivate('lock')
    def lock(self):
        if not self.enable or self._v_active or not self.skin_name:
            log.debug('deployment skin not enabled')
            return

        portal = getToolByName(self, 'portal_url').getPortalObject()
        skins  = getToolByName(self, 'portal_skins')
        
        if not self.skin_name in skins.getSkinSelections():
            raise RuntimeError("Invalid Skin for Deployment %s"%self.skin_name)

        try:
            request = self.REQUEST
        except AttributeError:
            request = {}
        
        self._v_saved_skin_name = portal.getSkinNameFromRequest(request) \
                                  or skins.getDefaultSkin()
        portal.changeSkin( self.skin_name )
        self._v_active = 1

    def _setSkin(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.changeSkin( self.skin_name )

    security.declarePrivate('unlock')        
    def unlock(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        skins = portal.portal_skins
        skin_name = self._v_saved_skin_name or skins.getDefaultSkin()
        portal.changeSkin( skin_name )
        self._v_saved_skin_name = None
        self._v_active = False
        
    def manage_afterAdd(self, item, container):
        self.skin_name  = getToolByName(self, 'portal_skins').getDefaultSkin()	

    #################################
    security.declarePrivate('getInfoForXml')
    def getInfoForXml(self):
        return {'attributes':{ 'skin_name':self.skin_name }, 'enable':bool( self.enable )  }


class InvalidUserDatabase(AttributeError): pass

class SiteChainUser(SimpleItem):
    """
    sign on a user during the course of a request.
    this user will be used during the mastering process.
    """

    meta_type = 'Site Chain User'
    id = 'site_user'
    enable = 0
    userid = None
    udb_path = None

    security = ClassSecurityInfo()
    
    def edit(self, enable, user, udb_path):
        
        self.enable = not not enable        
        self.userid = user
        
        try:
            if udb_path == 'special':
                assert user in ('nobody', 'system')
            else:
                udb = self.unrestrictedTraverse(udb_path)
                assert udb.id == 'acl_users'
        except:
            raise InvalidUserDatabase(" invalid user database or user ")
        
        self.udb_path = udb_path

    security.declarePrivate('lock')
    def lock(self):

        if not self.enable or not self.userid or not self.udb_path:
            log.debug('not chaining user')
            return
        
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl import SpecialUsers

        # we can restore the existing user latter if need be, we don't for now.
        current_user = getSecurityManager().getUser()
        current_udb_path  = aq_parent(aq_inner(current_user)).getPhysicalPath()
        current_userid = current_user.getId()

        # get the new user
        
        if self.udb_path == 'special':
            user = getattr( SpecialUsers, self.userid )
            user = user.__of__( self.unrestrictedTraverse('/') )
        else:             
            udb = self.unrestrictedTraverse(self.udb_path)
            user = udb.getUser(self.userid).__of__(udb)

        # sign on the new user
        try: req = self.REQUEST
        except: req = None
        newSecurityManager(req, user) 

    security.declarePrivate('unlock')        
    def unlock(self):
        pass

    security.declarePrivate('getInfoForXml')
    def getInfoForXml(self):
        return {'attributes':{ 'user' : self.userid or '',
                               'udb_path' : self.udb_path or ''},
                               'enable' : bool( self.enable ) } 
    
