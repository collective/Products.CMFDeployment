"""
$Id: deletion.py 1231 2006-03-14 05:53:43Z hazmat $
"""


from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addDeletionSource( self, id, title="", RESPONSE=None):
    """ add a deletion source
    """
    source = DeletionSource( id, title )
    self._setObject( id, source )

    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')

addDeletionSourceForm = DTMLFile('../ui/SourceDeletionForm', globals())

class DeletionSource( SimpleItem ):
    """
    stores records for content deleted through the portal lifecycle.
    """

    __implements__ = IContentSource

    meta_type = "Deletion Source"
    
    manage_options = (
        {'label':'Source',
         'action':'source'},
        )
    source = DTMLFile('../ui/ContentSourceDeletionView', globals())
    
    def __init__(self, id, title=""):
        self.id = id
        self._records = []

    def getContent( self ):
        return self.destructiveIter()

    def listContent( self ):
        return tuple( self._records )
        
    def destructiveIter(self):
        for rec in self._records:
            yield rec
        self._records = []

    def addRecord( self, record ):
        self._records.append( record )
        self._p_changed = 1



    
