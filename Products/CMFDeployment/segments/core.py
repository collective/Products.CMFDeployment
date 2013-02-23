"""
$Id: core.py 1155 2006-02-06 19:52:39Z hazmat $
"""

from interfaces import *

#################################

OUTPUT_FILTERED = object()

# internal marker value to pipe execution
_OUTPUT_FINISHED = object()

#################################

class Pipeline( object ):

    __implements__ = IPipeline 
    
    def __init__(self, **kw):
        self.steps = kw.get('steps') or []
        self.variables = kw
        self.services = {}
        
    def __iter__(self):
        for s in self.steps:
            yield s

    def process( self, context ):
        for s in self:
            context = s.process( self, context )

class PolicyPipeline( Pipeline ): pass


class PipeExecutor( object ):
    """
    support for pipes include producer/filters/conditional branches segments
    """

    def __init__(self, steps ):
        self.steps = list( steps )
        self.context_iterator = None
        self.producer_idx = 0

    def insert( self, idx, step ):
        self.steps.insert( idx, step )
        
    def process( self, pipeline, context ):
        idx = 0
        origin_ctx = context
        
        while context is not _OUTPUT_FINISHED:

            step = self.steps[idx]

            if isinstance( step, Producer ):
                if self.context_iterator is not None:
                    raise RuntimeError("only one producer per pipeline atm")
                self.context_iterator = step.process( pipeline, context )
                context = self.getNextContextObject()
            elif isinstance( step, Consumer ):
                step.process( pipeline, context )
                context = self.getNextContextObject()
                idx = self.producer_idx
            elif isinstance( step, Filter ):
                value = step.process( pipeline, context )
                if value is OUTPUT_FILTERED:
                    context = self.getNextContextObject()
                    idx = self.producer_idx
                elif value is None: 
                    pass
                    #print "filter returned none", step, value
                else:                    
                    context = value
            elif isinstance( step, PipeSegment ):
                context = step.process( pipeline, context )
            else:
                print "Unknown Step", step

            idx += 1
            
        return origin_ctx

    def getNextContextObject( self ):
        if self.context_iterator is None:
            return _OUTPUT_FINISHED
        try:
            return self.context_iterator.next()
        except StopIteration:
            return _OUTPUT_FINISHED
            
                
class BaseSegment( object ):
    
    def process( self, pipeline, ctxobj ):
        raise NotImplemented

class PipeSegment( BaseSegment ):

    __implements__ =  IPipeSegment 

class Producer( PipeSegment ):

    __implements__ = IProducer 

class Consumer( PipeSegment ):

    __implements__ = IConsumer

class Filter( PipeSegment ):
    
    __implements__ = IFilter


class VariableAggregator( Consumer ):
    """
    consume contexts into a variable
    """

    def __init__(self, variable_name=""):
        self.variable_name = variable_name

    def process(self, pipeline, ctxobj ):
        #print "adding", ctxobj, "to", self.variable_name
        values = pipeline.variables.setdefault( self.variable_name, [] )
        values.append( ctxobj )
        return None

class VariableIterator( Producer ):
    """
    producer which iterate values from a variable
    """

    def __init__(self, variable_name ):
        self.var_name = variable_name

    def process( self, pipeline, ctxobj ):
        for value in pipeline.variables.get( self.var_name, () ):
            yield value


## class ConditionalBranch( PipeSegment ):

##     def __init__(self, branches ):
##         assert isinstance( branches, list)
##         self.branches = branches

##     def addBranch( self, condition, step ):
##         self.branches.append( ( condition, step ) )

##     def process( self, pipeline, ctxobj ):
##         for condition, step in self.branches:
##             if condition( ctxobj ):
##                 return step( pipeline, ctxobj )

