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
enables author link rendering in plone.

$Id: author.py 1253 2006-03-20 08:55:11Z hazmat $
"""


from Products.CMFDeployment.Namespace import *
from base import SiteBaseResource
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment.URIResolver import clstrip, extend_relative_path, normalize
from Products.CMFDeployment.DeploymentExceptions import InvalidResource
from directoryview import cook
from Products.CMFDeployment.Log import LogFactory

log = LogFactory('AuthorIdxR')

addAuthorIndexesRuleForm = DTMLFile('../ui/ResourceAuthorsIndexAddForm', globals())

def addAuthorIndexesRule(self, id, view_path, source_path, deployment_path, RESPONSE=None):
    """
    add an authors indexes rule
    """
    view_path = view_path.strip()
    rule = AuthorIndexesRule( id,
                               view_path,
                               source_path,
                               deployment_path )    

    container = self.this()    
    rule.isValid( container ) # raises
    self._setObject( id, rule )
    
    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')


class ContentRender( object ):

    def __init__(self, renderer ):
        self.renderer = renderer

    def __call__(self, content=None):
        return renderer()

class AuthorIndexesRule( SiteBaseResource ):

    meta_type = "Author Indexes Rule"
    security = ClassSecurityInfo()

    #icon = 'misc_/PageTemplates/.gif'
    xml_factory = "addAuthorIndexesRuleRule"

    index_name = 'Creator'
    icon_path = 'user.gif'
    
    # zmi icon
    def icon(self):
        return getToolByName(self, 'portal_url')(relative=1)+'/'+self.icon_path

    def isValid(self, container):
        # we should be singleton in a policy, no reason to do otherwise and
        # deploy this content multiple times.
        if len(container.objectValues( self.meta_type )) > 0:
            raise InvalidResource("only one author index per policy")
        return True
    
    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self, view_path, source_path, deployment_path, RESPONSE=None):
        """
        edit authors index rule
        """
        SiteBaseResource.edit( self, view_path, source_path, deployment_path)

        if RESPONSE is not None:
            container = self.getParentNode()
            return RESPONSE.redirect("%s/manage_main"%container.absolute_url())
        
    def getDescriptors(self, since_time=None):
        """
        return descriptors for every unique value of a catalog index as resources

        this one utilizes the Creator catalog index.

        only field indexes can be deployed in this way.

        stores persistent data as annotation on the policy
        
        since_time not honored,
        however via comparisons to the indexes's histogram. 
        
        """
        portal = getToolByName( self, 'portal_url').getPortalObject()
        try:
            request = self.REQUEST
        except:
            log.warning("request not available, returning empty set")
            raise StopIteration
        
        view_path = self.view_path
        if view_path.startswith('/'):
            view_path = view_path[1:]

        source_path, deploy_path = self.source_path, self.deployment_path 
        uris = self.getDeploymentPolicy().getDeploymentURIs()
        vhost_path = uris.vhost_path

        mp = self.getDeploymentPolicy().getContentOrganization().getActiveStructure().getCMFMountPoint()
        base_path = '/'.join(mp.getPhysicalPath())
            
        # get rid of trailing and leading slashes and join to base path
        source_path = extend_relative_path(
                                              clstrip('/'.join(
                                                   (vhost_path, base_path, '/'.join(
                                                           filter(None,
                                                                  source_path.split('/'))))), '/')
                                              )

        for value in self.getValues( since_time ):
            if not value:
                continue
            assert '/' in deploy_path

            # initial content is portal, we change later to the bound method
            d = ContentDescriptor( portal )
            d.setContentPath(deploy_path)
            d.setFileName("%s.html"%value)
            
            v = "%s/%s"%(source_path, value)
            d.setSourcePath( normalize(v, '/')[1:] )

            # setup the values as a subpath variable to the resolved
            # view path
            renderer = request.traverse(
                d.getSourcePath()
                )
#                normalize( "%s/%s"%( self.view_path, value ),
#                           "/")[1:],
#                None
#                )

            if renderer is None:
                log.warning("invalid view for author idx %s"%(self.view_path))
                raise StopIteration

            d.content = None
            d.setRenderMethod( renderer )
            d.rule_id = self.getId()
            
            yield d


    def getValues(self, since_time=None):
        """
        returns index unique values, treats since time as a boolean,
        if true, return all values which did not exist or which have
        different counts then the last deployment run compares unindex
        uniquevalue counts, if false return all unique values.
        """
        catalog = getToolByName(self, 'portal_catalog')
        
        # grab the unindex directly
        indexes = [i for i in catalog.getIndexObjects() \
                   if i.getId() == self.index_name ]
        idx = indexes.pop()

        value_count_map = dict( idx.uniqueValues(withLengths=1) )
        history = self.getDeploymentHistory().getLast()

        if since_time is None:
            return value_count_map.keys()
            
        previous_count_map = getattr(history, "_annotations", {}\
                                     ).get('value_count_map_%s'%self.getId(),{})
        

        cur_history = self.getDeploymentHistory().getCurrent()
        #self.getAnnotation( cur_history, create=True )
        
        return [ k for k,v in value_count_map.items() \
                 if previous_count_map.get( k, 0 ) != v ]

    def cook(self, descriptor):
        renderer = descriptor.getRenderMethod()
        try:
            descriptor.setRendered( renderer() )
        except:
            log.warning("error while rendering author idx value %s"%(descriptor.source_path))
            descriptor.setGhost(1)
