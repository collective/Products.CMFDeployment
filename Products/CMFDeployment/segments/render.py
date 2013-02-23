from core import PipeSegment

class ContentRender( PipeSegment ):

    def process( self, pipe, descriptor):
        rules = pipe.services["ContentRules"]
        rules.cook( descriptor )
        return descriptor
    
