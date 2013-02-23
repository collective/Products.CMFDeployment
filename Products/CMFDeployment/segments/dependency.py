"""

Dependencies are the heart of the incremental deployment pipeline.

they are designed to answer a simple question, ie. if i deploy object A
what other objects do i need to deploy along with it, and conversely
if i delete object B what are there objects should i delete with it.

there are many examples of dependency relationships, and the dependency
engine delegates dependency specification to other components, primarily
content rules, and obtains the spec from a descriptor. some dependency
examples.

 - a document with embedded object references ( author, files ), etc.

 - a container that displays a listing view of its contents, is dependent
   on all of them.

its important to state that cmfdeployment is only concerned with dependencies
as pertains to the object's rendered views that will be deployed, ie. strictly
ui dependencies.

also the dependency manager participates as a component in a deployment
pipeline and dependencies deployed must still pass all filters, and match
to a content rule, else they won't be deployed by the system. also its assumed
that the dependency engine is injecting dependencies into a pipeline that
has a processing segment that will stop introduction of duplicates.

dependency injection via use of a dependency content source.

a design goal is to keep the dependency manager as simple as possible, and
thus stateless as previous experiments with automatic tracking of content
have show it to be overly complex (at least without an event system ;-) ).
so descriptors are responsible for returning both dependencies and reverse
dependencies. this also eases consideration of dynamic dependencies.

Author: Kapil Thangavelu <hazmat@objectrealms.net>
$Id: dependency.py 1155 2006-02-06 19:52:39Z hazmat $
"""

from core import PipeSegment
from Products.CMFDeployment import DefaultConfiguration

class DependencyManager( object ):

    dependency_source = None
        
    def processDeploy( self, pipe, descriptor ):
        #cpath = "/".join(descriptor.getContent().getPhysicalPath())        
        #print "Proceessing Deploy For", cpath
        
        source = self.getDependencySource( pipe )
        if not source:
            return descriptor
        
        # (re)deploy objects that depend on descriptor
        for rdep in descriptor.getReverseDependencies():
            #print "adding rdep", rdep
            source.addDependency( rdep )

        return descriptor

    def processRemoval( self, pipe, record ):
        source = self.getDependencySource( pipe )
        if not source:
            return record

        policy = pipe.services['DeploymentPolicy']
        # pass policy in as context
        for rdep in record.getReverseDependencies( policy ):
            source.addDependency( rdep )

        return record

    def getDependencySource(self, pipe):

        if self.dependency_source is not None:
            return self.dependency_source
        
        self.dependency_source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DependencySource, None )

        if self.dependency_source is None:
            raise AttributeError("no dependency source in policy")
        
        return self.dependency_source


class DeployDependencyInjector( PipeSegment, DependencyManager ):

    process = DependencyManager.processDeploy


class RemovalDependencyInjector( PipeSegment, DependencyManager ):

    process = DependencyManager.processRemoval
