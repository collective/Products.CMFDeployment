"""
$Id: dependency.py 1105 2006-01-01 09:51:55Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.DeploymentInterfaces import IContentSource

def addDependencySource( self,
                         id='dependency_source',
                         title='',
                         RESPONSE=None):
    """
    add dependency deployment source
    """
    source = DependencySource( id, title )
    self._setObject( id, source )

    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')

addDependencySourceForm = DTMLFile('../ui/SourceDependencyForm', globals())

class DependencySource( SimpleItem ):
    """
    content dependency source
    """
    
    meta_type = "Dependency Source"
    
    __implements__ = IContentSource

    def _v_queue( self ):
        self._v_queue = v = []
        self._p_changed = 1
        return v

    _v_queue = ComputedAttribute( _v_queue )

    def __init__(self, id, title=""):
        self.id = id
        self.title = title

    def getContent(self):
        return self.destructiveIter()

    def destructiveIter(self):
        for brain in self._v_queue:
            yield brain
        self._v_queue = []
        
    def addDependency( self, brain ):
        self._v_queue.append( brain )
        
InitializeClass( DependencySource )

