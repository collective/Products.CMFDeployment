##################################################################
#
# (C) Copyright 2004-2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
# All Rights Reserved
#
# This file is part of CMFDeployment.
#
# CMFDeployment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFDeployment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
$Id: atcontent.py 1990 2007-07-12 15:09:19Z hazmat $
"""

from Products.Archetypes import public as atapi
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from Products.CMFDeployment import utils as deploy_utils
from Products.CMFDeployment.Namespace import CMFCorePermissions

from Products.CMFCore.Expression import Expression
from Products.CMFCore import utils

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile, InitializeClass

from default import ContentRule

def addATContentRule(self, id, extension_expression, condition, view_method, ghost=0, aliases=(), children=(), RESPONSE=None):
    """
    add an archetype rule
    """
    atrule = ArchetypeContentRule(id,
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
    
addATContentRuleForm = DTMLFile('../ui/ContentRuleATAddForm', globals())

class ArchetypeContentRule( ContentRule ):

    meta_type = "Archetype Content Rule"
    xml_factory = "addATContentRule"
    
    __implements__ = IContentRule

    security = ClassSecurityInfo()


    def isValid(self, content, context):
        if not isinstance( content, (atapi.BaseContent, atapi.BaseFolder) ):
            return False
        elif self.condition_text and not self.condition( context ):
            return False
        return True

    def process(self, descriptor, context):
        descriptor = ContentRule.process( self, descriptor, context )
        resource_descriptors = self.getSchemaResources( descriptor )
        for rd in resource_descriptors:
            descriptor.addChildDescriptor( rd )
        return descriptor

    def getSchemaResources( self, descriptor):
        content = descriptor.getContent()
        schema = content.Schema()
        #content_path = content.absolute_url(1)
        factory = None
        
        for field in schema.filterFields():
            if isinstance( field, (atapi.ImageField, atapi.FileField)):
                value = field.get( content )
            else:
                continue
            if not value or isinstance(value, str):
                continue
            if factory is None:
                factory = DescriptorFactory( self.getDeploymentPolicy() )
            descriptor = factory( value )
            
            # xxx this isn't actually used :-( but it needs to be resolvable
            # file objects get special treatment.  the system will work without
            # but throw a spurious log message.
            descriptor.setRenderMethod('index_html')
            descriptor.setBinary( True )
            
            resource_name = self.getResourceName( value )
            #descriptor.setFileName("%s/%s"%(content.getId(), resource_name) )
            descriptor.setFileName( resource_name )

            yield descriptor

    def getResourceName(self, content):
        return deploy_utils.guess_filename( content )
    

InitializeClass(ArchetypeContentRule)

