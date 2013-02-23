"""
$Id: interfaces.py 1109 2006-01-03 07:23:47Z hazmat $
"""

__all__ = ['IPipeline', 'IPipeSegment', 'IProducer', 'IConsumer', 'IFilter', 'implements']

try:
    from zope.interface import Interface, Attribute, implements
except ImportError:
    from Interface import Interface, Attribute
    def implements( iface ): pass


class IPipeline( Interface ):
    
    services = Attribute("mapping of services available in the pipeline")
    
    variables = Attribute("mapping of variables defined in the pipeline")

    def process( context ):
        """
        process the given context through the pipeline
        """
    
class IPipeSegment( Interface ):
    
    def process( pipeline, ctxobj ):
        """
        process the given context object through the segment, returning
        the context object as a result
        """

class IProducer( IPipeSegment ):
    """
    A pipeline segment that iterates multiple return values for
    a given context object.
    """

class IConsumer( IPipeSegment ):
    """
    a pipeline endpoint/sink, consumes context objects, no return
    value.
    """

class IFilter( IPipeSegment ):
    """
    a pipeline segment that conditionally filters input, if the output
    is filtered, returns OUTPUT_FILTERED marker value, and subsequent
    segments are not executed, else return the context object for the
    next segment.
    """


