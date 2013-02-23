"""
An External Method for content deployment as XML

depends on marshall product (k_vertigo-pluggable-ns branch)

"""

from Products.CMFCore.utils import getToolByName
from Products.Marshall.handlers import XmlMarshaller

def deploy_xml( self ):
    content = self
    marshaller = XmlMarshaller()
    return marshaller.marshall( content )[-1]


    
