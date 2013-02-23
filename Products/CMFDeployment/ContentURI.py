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
Purpose: 

Persistent URI Database

 allows for configuration of target path for uri normalization

 additional notes on normalization/resolution in URIResolver.py

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
$Id: ContentURI.py 1990 2007-07-12 15:09:19Z hazmat $
License: GPL

"""
from Namespace import *
from URIResolver import URIResolver
from BTrees.OOBTree import OOBTree

class ContentURI(SimpleItem, URIResolver):

    meta_type = 'Content URI Resolver'

    manage_options = (

        { 'label':'Settings',
          'action':'content_uri_overview' },

        { 'label':'Policy',
          'action':'../manage_workspace'}
        )
    
    security = ClassSecurityInfo() 

    xml_key = "resolver"
    
    content_uri_overview = DTMLFile('ui/ContentURIOverview', globals())
    
    def __init__(self, id):
        self.id = id
        ContentURI.inheritedAttribute('__init__')(self)

    security.declarePrivate('clear')
    def clear(self):
        self.uris = OOBTree()

    security.declarePrivate('clone')
    def clone(self, persistent=0):
        
        r = URIResolver()
        if persistent:
            r.__dict__.update(self.__dict__) # create a shared ref to the uri db
        else:
            r.source_host = self.source_host
            r.target_path = self.target_path
            r.vhost_path   = self.vhost_path
            r.link_error_url = self.link_error_url
            r.external_resolver_path = self.external_resolver_path
            r.relative_target_resolution = self.relative_target_resolution
            r.enable_text_resolution = self.enable_text_resolution
        return r
    
    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def editContentURI(self,
                       target_path,
                       vhost_path='',
                       link_error_url='deploy_link_error',
                       external_resolver_path='',
                       relative_target_resolution=False,
                       enable_text_resolution=False,
                       REQUEST=None ):
        """ edit """


        target_path = target_path.strip()
        if not target_path.endswith('/'):
            target_path += '/'
            
        self.target_path = target_path
        self.vhost_path  = vhost_path.strip()
        self.link_error_url = link_error_url.strip()
        self.relative_target_resolution = bool( relative_target_resolution )
        self.external_resolver_path = external_resolver_path.strip()
        self.enable_text_resolution = bool( enable_text_resolution )
        
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('content_uri_overview')

        
    # protect some inherited methods
    security.declarePrivate('addResource')
    security.declarePrivate('resolve')
    security.declareProtected('Manage portal', 'pprint')
    
    security.declarePrivate('getInfoForXml')
    def getInfoForXml(self):
        
        return {'target_path': self.target_path,
                'vhost_path' : self.vhost_path,
                'link_error_url': self.link_error_url,
                'external_resolver_path' : self.external_resolver_path,
                'relative_target_resolution' : bool( self.relative_target_resolution ),
                'enable_text_resolution' : bool( self.enable_text_resolution ) }
    

    security.declarePrivate('fromStruct')
    def fromStruct( self, struct ):
        struct = dict( [ (str(k),v) for k,v in struct.items() ])        
        self.editContentURI( **struct )

    
InitializeClass(ContentURI)
