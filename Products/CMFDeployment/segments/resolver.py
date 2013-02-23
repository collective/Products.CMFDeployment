"""
$Id: resolver.py 1114 2006-01-03 09:59:50Z hazmat $
"""

from core import PipeSegment

class ResolveContent( PipeSegment ):
    """
    resolve the rendered content
    """
    
    def process( self, pipe, descriptor ):

        if descriptor.isGhost():
            return descriptor

        resolver = pipe.services['ContentResolver']
        resolver.resolve( descriptor )

        return descriptor
    
class ResolverDatabase( PipeSegment ):
    """
    add the content to the uri resolver database
    """

    def process( self, pipe, descriptor ):
        
        resolver = pipe.services['ContentResolver']
        resolver.addResource( descriptor )
        return descriptor

class ResolverRemoval( PipeSegment ):
    """
    remove the content from the uri resolver db
    """

    def process( self, pipe, descriptor ):
        resolver = pipe.services['ContentResolver']
        resolver.removeResource( descriptor )
        return descriptor        
        
    

