"""
$Id: catalog.py 1957 2007-05-14 07:26:27Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

from base import BaseSource
from zope.interface import implements

def addPortalCatalogSource( self,
                            id,
                            title='',
                            RESPONSE=''):
    """ riddle me this, why is a doc string here..
        answer: bobo
    """

    self._setObject( id, PortalCatalogSource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addPortalCatalogSourceForm = DTMLFile('../ui/SourceCatalogForm', globals() )

class PortalCatalogSource(BaseSource):

    meta_type = 'Catalog Content Source'

    implements(IContentSource)

    manage_options = (
        {'label':'Source',
         'action':'source'},        
        )

    xml_factory = 'addPortalCatalogSource'

    icon_path = "book_icon.gif"
    
    source = DTMLFile('../ui/ContentSourceView', globals())

    def __init__(self, id, title='retrieves content from portal_catalog'):
        self.id = id
        self.title = title
        
    def getContent(self):
        catalog = getToolByName(self, 'portal_catalog')
        objects = catalog()
        return objects


def addIncrementalCatalogSource( self,
                                 id,
                                 title='',
                                 RESPONSE=''):
    """ add an incremental catalog source
    """

    self._setObject( id, IncrementalCatalogSource(id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addIncrementalCatalogSourceForm = DTMLFile('../ui/SourceIncrementalCatalogForm', globals() )

class IncrementalCatalogSource(BaseSource):

    meta_type = 'Incremental Catalog Content Source'

    implements(IContentSource)

    manage_options = (
        {'label':'Source',
         'action':'source'},
        {'label':'Results',
         'action':'results'}
        )

    xml_factory = 'addIncrementalCatalogSource'

    icon_path = "book_icon.gif"
    
    source = DTMLFile('../ui/ContentSourceIncrementalView', globals())
    results = DTMLFile('../ui/ContentSourceIncrementalResultsView', globals())    

    def __init__(self, id, title='retrieves content from portal_catalog'):
        self.id = id
        self.title = title

    def getLastDeploymentTime( self ):
        last_deployment_time = self.getDeploymentHistory().getLastTime()
        return last_deployment_time

    def getLastDeploymentTimeIdx( self ):
        return ''
#        return self.portal_catalog._catalog.getIndex('content_modification_date')
#    ._convert(
#            self.getLastDeploymentTime()
#            )        

    def getContent(self):
        """
        return all content modified/created since the last deployment.
        """
        catalog = getToolByName(self, 'portal_catalog')

        object_paths = [p.strip() for p in self.REQUEST.get("debug_deploy_paths", "").split("\n")]
        object_paths = filter(None, object_paths)

        if object_paths:
            query = self._get_debug_query(path=object_paths.pop())
            incremental = True
        else:
            query = self._get_incremental_query()
            if query:
                incremental = True
            else:
                incremental = False
        
        objects = catalog(**query)
        # the catalog has a rather fun 'feature' if the query doesn't match anything,
        # it returns everything .. lovely .. detect and return empty set
        if incremental and len(objects) == len(catalog):
            return ()
        return objects


    def _get_debug_query(self, **kw):
        return kw

    
    def _get_incremental_query(self):
        
        last_deployment_time = self.getLastDeploymentTime()
        reset_date = self.getDeploymentPolicy().getResetDate()

        if not reset_date and last_deployment_time is not None:
            query = {'content_modification_date': {'query':last_deployment_time, 'range':'min'} }
        else:
            query = {}
        return query
    

