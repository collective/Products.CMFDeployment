"""
A Content Rule for AT Containers

$Id: atcontainer.py 1788 2006-12-14 23:45:50Z hazmat $
"""

from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from Products.CMFDeployment import utils

from atcontent import ArchetypeContentRule

def addATContainerRule(self, id, extension_expression, condition, view_method, ghost=0, aliases=(), children=(), RESPONSE=None):
    """
    add an archetype rule
    """
    atrule = ATContainerRule(id,
                             extension_expression=extension_expression,
                             condition=condition,
                             view_method=view_method,
                             ghost=ghost,
                             aliases=aliases)

    self._setObject(id, atrule)

    rule = self._getOb( id )
    for child_view in children:
        # sigh.. tired.. late nite.. hack.. works..
        child_view = dict( [ (str(k),v) for k,v in child_view.items() ])        
        rule.addChildView( **child_view )
        
    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')
    
addATContainerRuleForm = DTMLFile('../ui/ContentRuleATContainerAddForm', globals())


class ATContainerRule( ArchetypeContentRule ):

    meta_type = "AT Container Rule"
    xml_factory = "addATContainerRule"

    def process(self, descriptor, context):
        # determines the default view of a container and if a container is a ghost or not
        # based on whether the default view is from another content object thats deployable,
        # if it is then we claim it as a reverse dependency. if its an acquired view or
        # contained page template, we handle as normal, if we can't find a folder default
        # view, fallback to normal default rendering.

        descriptor = ArchetypeContentRule.process( self, descriptor, context )
        
        render_method = descriptor.getRenderMethod()
        container = descriptor.getContent()

        if not render_method:
            plone_tool = getToolByName( self, 'plone_utils')

            # plone 2.1 compatiblity check
            if hasattr( plone_tool, 'getDefaultPage'):
                render_method = plone_tool.getDefaultPage( container )
                
            # for 2.0 if there is an index html contained then use that
            elif container._getOb( 'index_html', None ) is not None:
                render_method = 'index_html'

            if render_method:
                descriptor.setRenderMethod( render_method )
            
        if render_method:
            renderer = container._getOb( render_method, None )
            
            # if its contentish make it a dependency
            if hasattr( aq_base( renderer ), 'portal_type'): 
                dependencies = descriptor.getReverseDependencies()
                dependencies.append( renderer )
                # this doesn't apply to any child views.
                descriptor.setGhost( True )                

        return descriptor
    
InitializeClass(ATContainerRule)
