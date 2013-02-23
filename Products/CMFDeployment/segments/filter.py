"""
$Id: filter.py 1155 2006-02-06 19:52:39Z hazmat $
"""

from Products.CMFDeployment.ContentIdentification import getFilterExprContext, ContentFilter as cFilter
from core import Filter, OUTPUT_FILTERED

class ContentFilter( Filter ):

    def process( self, pipe, content ):
        restricted = self.getRestrictedIds( pipe )
        mount_length = pipe.variables['mount_length']
        
        portal = self.getPortal( pipe )
        
        path = "/".join( content.getPhysicalPath() )[mount_length:]
        #print "10"*10
        #print "Path Filter", restricted, path
        for rst in restricted:
            if rst in path:
                #print "Filtered"
                return OUTPUT_FILTERED

        ec = getFilterExprContext( content, portal )

        for f in self.getFilters( pipe ):
            if isinstance( f, cFilter):
                if not f.filter(ec):
                    #log.debug('Filtered Out (%s) (%s)->(%s)'%(f.getId(), c.portal_type, c.getPath()))
                    return OUTPUT_FILTERED
            elif not f(content):
                #log.debug('Scripted Out (%s) (%s)->(%s)'%(s.getId(), c.portal_type, c.getPath()))
                return OUTPUT_FILTERED
        return content
        
    def getRestrictedIds(self, pipe):
        structure = pipe.services['ContentOrganization'].getActiveStructure()
        return tuple( structure.restricted )

    def getFilters(self, pipe):
        return pipe.services['ContentIdentification'].filters.objectValues()

    def getPortal(self, pipe):
        return pipe.services['ContentOrganization'].portal_url.getPortalObject()

    def getFilters( self, pipe ):
        return pipe.services['ContentIdentification'].filters.objectValues()
        

        
