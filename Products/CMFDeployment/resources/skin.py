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
$Id: skin.py 1225 2006-03-13 22:48:47Z hazmat $
"""

import re
from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.Log import LogFactory
from Products.CMFDeployment.URIResolver import clstrip, extend_relative_path
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFCore.FSObject import FSObject

from base import SiteBaseResource
from directoryview import cook

log = LogFactory("SkinResourceRule")

addSkinResourceRuleForm = DTMLFile('../ui/ResourceSkinAddForm', globals())

def addSkinResourceRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
    """
    add all css, js, and images from a site's skin 
    """
    
    view_path = view_path.strip()
    
    rule = SiteSkinResourceRule( id,
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

class ContainerMap( object ):

    def __init__(self, containers):
        self.containers = containers
        self._object_map = {}
        
        for idx in range(len( containers )):
            container = containers[idx]
            for oid in container.objectIds():
                self._object_map[oid]=idx

    def match(self, pattern):
        regex = re.compile(pattern)
        return [ self.containers[ self._object_map[ oid ]]._getOb( oid ) \
                 for oid in self._object_map.keys() \
                 if regex.match( oid ) is not None ]


    def test(self, pattern):
        regex = re.compile(pattern)
        return [ (oid, self._object_map[ oid ]) \
                 for oid in self._object_map.keys() \
                 if regex.match( oid ) is not None ]
    
    def clear(self):
        del self.containers

class SiteSkinResourceRule( SiteBaseResource ):

    meta_type = "SiteSkin Resource Rule"
    security = ClassSecurityInfo()
    xml_factory = "addSkinResourceRule"

    test_rule_results = DTMLFile('../ui/ResourceSkinTest', globals() )

    icon = 'misc_/CMFDeployment/resource_directory_view.gif'
    
    manage_options = SiteBaseResource.manage_options + (
                {'label':'Test',
                 'action':'test_rule_results'},
                )

    def edit(self, view_path, source_path, deployment_path, RESPONSE=None):
        """
        edit
        """
        
        SiteBaseResource.edit( self, view_path, source_path, deployment_path)
        
        # test the regex for compilation validity
        re.compile(self.view_path)
        
        if RESPONSE is not None:
            return RESPONSE.redirect("%s/test_rule_results"%(self.absolute_url()))
    
    security.declarePrivate('getSkinDirectories')
    def getSkinDirectories(self):
        skins_tool = getToolByName( self, 'portal_skins')
        skin_chain = self.getDeploymentPolicy().getContentMastering().site_skin
        
        if skin_chain.enable and skin_chain.skin_name:
            skin_name = skin_chain.skin_name
        else:
            skin_name = skins_tool.getDefaultSkin()

        skin_path = skins_tool.getSkinPath( skin_name )
        if skin_path is skin_name:
            log.warning("Skin not found for resource extraction - %s"%skin_name)

        res = []
        for container_id in skin_path.split(','):
            res.append( skins_tool._getOb( container_id ) )

        # we populate based on reverse lookup order to allow for normal skin overriding
        # behavior.
        res.reverse() 
        return res

    security.declarePrivate('getDescriptors')
    def getDescriptors(self, since_time):
        
        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        
        base_path = '/'.join(mp.getPhysicalPath())
        
        directories = self.getSkinDirectories()
        if directories is None:
            raise StopIteration            

        source_path, deploy_path = self.source_path, self.deployment_path 
        vhost_path = self.getDeploymentPolicy().getDeploymentURIs().vhost_path
            
        # get rid of trailing and leading slashes and join to base path
        source_path = extend_relative_path(clstrip('/'.join( (vhost_path, base_path, '/'.join(filter(None, source_path.split('/'))))), '/'))
        deploy_path = '/'.join(filter(None, deploy_path.split('/')))
        
        container_map = ContainerMap( directories )

        if since_time is not None:
            since_ticks = since_time.timeTime()
            
            def time_filter( dvo ):
                if isinstance( dvo, FSObject):
                    return since_ticks < dvo._file_mod_time 
                else:
                    return since_time < dvo.bobobase_modification_time()
        else:
            def time_filter( dvo ): return True                

        res = []
        for c in container_map.match( self.view_path ):
            #if not time_filter( c ):
            #    continue

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

    security.declarePrivate('cook')
    def cook(self, descriptor):
        return cook( self, descriptor )

    def getTestResults(self):
        """
        """
        directories = self.getSkinDirectories()
        container_map = ContainerMap( directories )

        results = container_map.test( self.view_path )
        results.sort()
        return results

        
        
InitializeClass( SiteSkinResourceRule )
