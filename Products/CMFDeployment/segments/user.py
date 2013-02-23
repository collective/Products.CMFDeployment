"""

Segments for changing user during deployment to configured deployment user,
and changing it back after deployment.

$Id: user.py 1144 2006-01-31 05:35:40Z hazmat $
"""

from core import PipeSegment

class UserLock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_user.lock()

class UserUnlock( PipeSegment ):

    def process( self, pipe, context ):
        rules = pipe.services['ContentRules']
        rules.site_user.unlock()
        
