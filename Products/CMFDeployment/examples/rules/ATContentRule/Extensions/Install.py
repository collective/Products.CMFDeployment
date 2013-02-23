from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from StringIO import StringIO
from Products.ATContentRule import PROJECT_NAME

def install( self ):
    
    out = StringIO()
    installTypes(self, out, listTypes( PROJECT_NAME ), PROJECT_NAME)
    return 'Installed'
