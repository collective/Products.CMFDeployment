"""

Segments for changing skin during deployment to configured deployment skin,
and changing it back after deployment.

$Id: skin.py 1144 2006-01-31 05:35:40Z hazmat $
"""

from core import PipeSegment

class SkinLock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_skin.lock()

class SkinUnlock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_skin.unlock()
        
