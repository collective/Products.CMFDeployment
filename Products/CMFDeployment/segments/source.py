"""
$Id: source.py 1957 2007-05-14 07:26:27Z hazmat $
"""

from Products.CMFDeployment import DefaultConfiguration
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

from core import Producer

class ContentSource(Producer):

    def process(self, pipe, ctxobj):
        for source in pipe.services["ContentIdentification"].sources.objectValues():
            for content in source.getContent():
                if isinstance( content, AbstractCatalogBrain ):
                    content = content.getObject()

                if content is None:
                    continue

                yield content

        dependency_source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DependencySource, None )

        if dependency_source is None:
            raise StopIteration

        for content in dependency_source.getContent():
            if content is None:
                continue
            yield content


class ContentPreviewDeletion( Producer ):

    def process( self, pipe, ctxobj ):
        source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DeletionSource, None
            )

        if source is None:
            raise StopIteration

        for record in source.listContent():
            yield record

class ContentDeletion( Producer ):

    def process(self, pipe, ctxobj):
        
        source = pipe.services['DeploymentPolicy']._getOb(
            DefaultConfiguration.DeletionSource, None
            )

        if source is None:
            raise StopIteration

        for record in source.getContent():
            yield record
            
