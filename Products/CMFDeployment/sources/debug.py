"""
$Id: catalog.py 1661 2006-09-14 02:38:47Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

from base import BaseSource
from zope.interface import implements

def addDebugSource( self,
                    id,
                    title='',
                    RESPONSE=''):
    """ Add a debug content source."""

    self._setObject(id, DebugSource(id, title))

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')


addDebugSourceForm = DTMLFile('../ui/SourceDebugForm', globals())


class DebugSource(BaseSource):

    meta_type = 'Catalog Content Source'

    implements(IContentSource)

    manage_options = (
        {'label':'Source',
         'action':'source'},        
        )

    xml_factory = 'addPortalCatalogSource'

    icon_path = "book_icon.gif"
    
    source = DTMLFile('../ui/ContentSourceView', globals())

    def __init__(self, id, title='Uses request values for content to deploy'):
        self.id = id
        self.title = title
        
    def getContent(self):
        object_paths = self.REQUEST.get("deploy_relative_path", ())
        catalog = getToolByName(self, "portal_catalog")
        catalog(path=object_paths)


def addDebugSource(self,
                   id,
                   title='',
                   RESPONSE=''):
    """ add a debug catalog source
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
        return self.portal_catalog._catalog.getIndex('content_modification_date')._convert(
            self.getLastDeploymentTime()
            )        

    def getContent(self):
        """
        return all content modified/created since the last deployment.
        """
        catalog = getToolByName(self, 'portal_catalog')

        last_deployment_time = self.getLastDeploymentTime()
        reset_date = self.getDeploymentPolicy().getResetDate()

        if not reset_date and last_deployment_time is not None:
            query = {'content_modification_date': {'query':last_deployment_time, 'range':'min'} }
        else:
            query = {}

        objects = catalog(**query)

        # the catalog has a rather fun 'feature' if the query doesn't match anything,
        # it returns everything .. lovely .. detect and return empty set
        if not reset_date and last_deployment_time is not None and len(objects) == len(catalog):
            return ()
        return objects
