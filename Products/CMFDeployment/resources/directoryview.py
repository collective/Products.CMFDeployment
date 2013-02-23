##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net
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
$Id: directoryview.py 1253 2006-03-20 08:55:11Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.Log import LogFactory
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.URIResolver import clstrip, extend_relative_path
from Products.CMFCore.FSObject import FSObject
from Products.CMFDeployment.DeploymentExceptions import InvalidDirectoryView
from Products.CMFDeployment.DefaultConfiguration import DEPLOYMENT_DEBUG
from DocumentTemplate import HTML

from Products.CMFDeployment.Log import LogFactory
log = LogFactory('Directory Views')


from base import SiteBaseResource

addDirectoryViewRuleForm = DTMLFile('../ui/ResourceDirectoryViewAddForm', globals())

def addDirectoryViewRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
    """
    add a directory view to the listing of deployable skin directories, after
    verifying the the view_path. 

    view_path - dv path relative to portal_skin
    deployment_path - path to deploy to relative to d. root
    source_path - the path that directory view appears relative to mount root,
       when doing uri resolution.
    """
    view_path = view_path.strip()
    
    rule = DirectoryViewRule( id,
                              view_path,
                              source_path,
                              deployment_path )    

    container = self.this()
    if rule.conflicts( container ):
        raise InvalidDirectoryView("View Path already exists")

    if not rule.isValid( container ):
        raise InvalidDirectoryView("%s is not valid"%str(view_path))

    self._setObject( id, rule )

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')
            

class DirectoryViewRule( SiteBaseResource ):

    meta_type = "Directory View Rule"
    security = ClassSecurityInfo()


    xml_factory = "addDirectoryViewRule"

    icon_path = 'folder_icon.gif'    
    # zmi icon
    def icon(self):
        return getToolByName(self, 'portal_url')(relative=1)+'/'+self.icon_path
    
    #################################
    # Begin SiteResource Interface Impl

    def getDescriptors(self, since_time):

        res = []
        
        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())

        dv = self.getDirectoryView(self.view_path)
        content = dv.objectValues()

        source_path, deploy_path = self.source_path, self.deployment_path 
        uris = self.getDeploymentPolicy().getDeploymentURIs()
        vhost_path = uris.vhost_path
            
        # get rid of trailing and leading slashes and join to base path
        source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))
        deploy_path = '/'.join(filter(None, deploy_path.split('/')))

        if since_time is not None:
            since_ticks = since_time.timeTime()
            def time_filter( dvo ):
                if isinstance( dvo, FSObject):
                    return since_ticks < dvo._file_mod_time 
                else:
                    return since_time < dvo.bobobase_modification_time()
        else:
            def time_filter( dvo ): return True
        
        for c in content:
            if not time_filter(c):
                continue
            d = ContentDescriptor(c)
            d.setContentPath(deploy_path)
            d.setFileName(c.getId())
            # XXX reconsider some of this manip
            v = "%s/%s"%(source_path, c.getId())
            d.setSourcePath('/'.join(filter(None,v.split('/'))))
            d.setRenderMethod('')
            d.rule_id = self.getId()
            res.append(d)
                
        return res

    security.declarePrivate('isValidDirectoryView')
    def isValid(self, container):
        """
        check to see if path is a portal_skin relative path
        leading to a directory view or objectmanager.
        """
        skins = getToolByName(container, 'portal_skins')
        components = filter(None, self.view_path.split('/'))

        d = skins
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                return 0
        if hasattr(aq_base(d), '_isDirectoryView'):
            return 1
        elif getattr(aq_base(d), 'isAnObjectManager'):
            return 1
        return 0        
    
    def cook(self, descriptor ):
        return cook(self, descriptor )

    # End SiteResource Interface Impl
    #################################
    
    security.declarePrivate('getDirectoryView')
    def getDirectoryView(self, path):
        """
        returns the directory view given by the portal skin
        relative 'path'
        """
        
        skins = getToolByName(self, 'portal_skins')
        components = filter(None, path.split('/'))

        d = skins
        for c in components:
            if hasattr(aq_base(d), c):
                d = getattr(d, c)
            else:
                raise InvalidDirectoryView(
                    "directory view does not exist %s of %s"%(c, path)
                    )
            
        assert not d is skins
        return d    
    
InitializeClass( DirectoryViewRule )


_fs_cookers = {}

def fs_dtml_cooker(self, descriptor, object):

    if object.meta_type.startswith('Filesystem'):
        object._updateFromFS()
    
    security = getSecurityManager()
    security.addContext(object)

    portal = getToolByName(object, 'portal_url').getPortalObject()

    try:
        r = HTML.__call__(object, None, portal)
        descriptor.setRendered(r)
    finally:
        security.removeContext(object)

def fs_image_cooker(self, descriptor, object):

    descriptor.setBinary(1)
    descriptor.setRendered(object._data)

def fs_zpt_cooker(self, descriptor, object):

    descriptor.setRendered(object())

def fs_file_cooker(self, descriptor, object):

    suffix = object.content_type.split('/')[0]
    if suffix in ('image', 'audio', 'video'):
        descriptor.setBinary(1)
    descriptor.setRendered(object._readFile(0))

def file_cooker(self, descriptor, object):

    descriptor.setBinary(1)
    if isinstance(object.data, str):
        data = object.data
    else:
        data = str(object.data)
    descriptor.setRendered(data)


_fs_cookers['Filesystem Image'] = fs_image_cooker
_fs_cookers['Filesystem DTML Method'] = fs_dtml_cooker
_fs_cookers['Filesystem Page Template'] = fs_zpt_cooker
_fs_cookers['Filesystem File'] = fs_file_cooker
# for instance space directory views
_fs_cookers['Image'] = file_cooker
_fs_cookers['DTML Method'] = fs_dtml_cooker
_fs_cookers['Page Template'] = fs_zpt_cooker
_fs_cookers['File'] = file_cooker

def registerDVRenderer( meta_type, renderer ):
    _fs_cookers[ meta_type ] = renderer

def cook(self, descriptor):

    object = descriptor.getContent()

    global _fs_cookers
    mt = getattr(object, 'meta_type', None)
    render = _fs_cookers.get(mt)
    
    if render is None:
        descriptor.setGhost(1)
        log.warning("couldn't find cooker for %s meta_type for %s id"%(mt,object.getId()))
        return

    try:
        render(self, descriptor, object)
    except:
        if DEPLOYMENT_DEBUG:
            import sys, pdb, traceback
            ec, e, tb = sys.exc_info()
            print ec, e
            traceback.print_tb( tb )
            #pdb.post_mortem( tb )               
        log.warning("error while render skin object %s"%str(object.getPhysicalPath()))
        descriptor.setGhost(1)

    return
