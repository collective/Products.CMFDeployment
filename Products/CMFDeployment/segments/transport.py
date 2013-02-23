"""
$Id: transport.py 1107 2006-01-02 12:05:40Z hazmat $
"""

from core import PipeSegment

class ContentTransport( PipeSegment ):

    def process( self, pipe, ctxobj ):
        transports = pipe.services['ContentTransports']
        organization = pipe.services['ContentOrganization']
        transports.deploy( organization.getActiveStructure() )
