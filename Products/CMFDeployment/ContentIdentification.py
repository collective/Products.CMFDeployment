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
Purpose: Identify Content that should be deployed
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: ContentIdentification.py 1398 2006-06-27 19:02:51Z hazmat $
"""

from Namespace import *
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import SecureModuleImporter, getEngine

from Products.CMFDeployment.utils import SerializablePlugin
from Log import LogFactory

from DeploymentInterfaces import *

log = LogFactory('ContentIdentification')


class ContentIdentification(Folder):

    meta_type = 'Content Identification'

    security = ClassSecurityInfo()

    __implements__ = (IContentSource,)

    manage_options = (
        
        {'label': 'Overview',
         'action': 'overview' },
        
        {'label':'Sources',
         'action':'sources/manage_main'},
        
        {'label':'Filters',
         'action':'filters/manage_main'},
        )

    security.declareProtected(Permissions.view_management_screens, 'overview')
    overview = DTMLFile('ui/IdentificationOverview', globals())

    xml_key = "identification"
    allowed_meta_types = ()
    
    def __init__(self, id):
        self.id = id

    security.declarePrivate('getContent')
    def getContent(self, mount_length=0):
        """
        retrieve deployable content brains
        """
        
        portal  = getToolByName(self, 'portal_url').getPortalObject()
        filters = self.filters.objectValues()
        structure = self.getDeploymentPolicy().getContentOrganization().getActiveStructure()
        restricted = structure.restricted
        
        skip = 0

        for c in self.sources.getContent():
            ## remove objects which reference restricted ids
            if mount_length:
                path = c.getPath()[mount_length:]
                for rst in restricted:
                    if path.count(rst) > 0:
                        log.debug('Restricted Id Filter (%s) (%s)->(%s)'%(rst, c.portal_type, c.getPath()))                        
                        skip = 1
                        break

            if skip:
                skip = 0
                continue
                                
            fc = getFilterExprContext(c,portal)
            
            for f in self.filters.objectValues():
                if f.meta_type == ContentFilter.meta_type:
                    if not f.filter(fc):
                        log.debug('Filtered Out (%s) (%s)->(%s)'%(f.getId(), c.portal_type, c.getPath()))
                        skip = 1
                        break
                elif not f(c):
                    log.debug('Scripted Out (%s) (%s)->(%s)'%(s.getId(), c.portal_type, c.getPath()))
                    skip = 1
                    break
                        
            yield c

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        if self._getOb('sources', None) is None:
            self._setObject('sources',  ContentSourceContainer('sources'))
        if self._getOb('filters', None) is None:
            self._setObject('filters',  ContentFilterContainer('filters'))

    def getInfoForXml(self):
        d = {}
        d.update( self.sources.getInfoForXml() )
        d.update( self.filters.getInfoForXml() )
        return d
    

InitializeClass(ContentIdentification)


#################################
# Source Container 

class ContentSourceContainer( OrderedFolder ):

    meta_type = 'Content Source Container'

    _product_interfaces = ( IContentSource, )

    manage_options = (
        {'label':'Content Sources',
         'action':'manage_main'},
        ) + App.Undo.UndoSupport.manage_options    
    
    def __init__(self, id, title="Content Sources"):
        self.id = id
        self.title = title
        
    def all_meta_types(self):
        """Delegate the call to IFAwareObjectManager"""
        return OrderedFolder.all_meta_types(self,
                                            interfaces=self._product_interfaces)

    def getContent( self ):
        for source in self.objectValues():
            for c in source.getContent():
                yield c

    def getInfoForXml( self ):
        res = []
        for source in self.objectValues():
            res.append( source.getInfoForXml() )
        return {'sources':res }

##     def manage_afterAdd(self, item, container):
        
##         import DefaultConfiguration
##         from sources import catalog
##         if not DefaultConfiguration.DEFAULT_CONTENT_SOURCE_ID in self.objectIds():
##             self._setObject(
##                 DefaultConfiguration.DEFAULT_CONTENT_SOURCE_ID,
##                 catalog.PortalCatalogSource(
##                   DefaultConfiguration.DEFAULT_CONTENT_SOURCE_ID )
##                 )
                                                 

InitializeClass( ContentSourceContainer )


#################################
# Filters

class ContentFilter(SerializablePlugin):

    meta_type = 'Content Filters'
    __implements__ = IContentFilter
    
    filter_manage_options = (
        {'label':'Edit Filter',
         'action':'manage_editContentFilter'},
        ) + App.Undo.UndoSupport.manage_options


    xml_factory = "addFilter"
    
    manage_options = filter_manage_options + SimpleItem.manage_options
    manage_editContentFilter = DTMLFile('ui/ContentExpFilterEditForm', globals())

    def __init__(self, id, text):
        self.id = id
        self.expression = Expression(text)
        self.expression_text = text
        
    def filter(self, context):
        return not not self.expression(context)

    def editFilter(self, expression_text, REQUEST=None):
        """ """
        self.expression_text = expression_text
        self.expression = Expression(expression_text)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

    def getInfoForXml(self):
        d = SerializablePlugin.getInfoForXml( self )
        del d['title']
        d['text' ] = self.expression_text
        d['product'] = "container"
        return d

InitializeClass( ContentFilter )


class ContentFilterContainer( OrderedFolder ):

    meta_type = 'Identification Filter Container'
    
    manage_options = (
        {'label':'Content Filters',
         'action':'manage_main'},
        ) + App.Undo.UndoSupport.manage_options
        
    content_filter_constructor_info = (
        {'name':ContentFilter.meta_type,
         'class':ContentFilter,
         'permission':CMFCorePermissions.ManagePortal,
         'action':'addFilterForm'},
        )

    def all_meta_types(self):
        import Products
        meta_types = [m for m in Products.meta_types if m['name']=='Script (Python)']
        meta_types.extend( self.content_filter_constructor_info )
        return meta_types
        
    addFilterForm = DTMLFile('ui/ExpressionFilterAddForm', globals())
    
    def __init__(self, id):
        self.id = id

    def addFilter(self, id, text, REQUEST=None):
        """ """
        self._setObject(id, ContentFilter(id, text))
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_main')

    def getInfoForXml(self):
        res = []
        for ob in self.objectValues( ContentFilter.meta_type ):
            res.append( ob )
        return {'filters':res}
        

def getFilterExprContext(object_memento, portal):

    data = {
        'portal_url':   portal.absolute_url(),
        'memento':      object_memento,
        'portal':       portal,
        'nothing':      None,
        'request':      getattr( portal, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        }
        
    return getEngine().getContext(data)

