##################################################################
#
# (C) Copyright 2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
$Id: __init__.py 1990 2007-07-12 15:09:19Z hazmat $
"""

from Products.Archetypes import public as atapi
from Products.CMFDeployment.Descriptor import DescriptorFactory
from Products.CMFDeployment.DeploymentInterfaces import IContentRule
from Products.CMFDeployment.Namespace import CMFCorePermissions

from Products.CMFCore.Expression import Expression
from Products.CMFCore import utils

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from App.special_dtml import DTMLFile
from AccessControl.class_init import InitializeClass


PROJECT_NAME = "ATContentRule"

xml_export_template = """
<mime id="%(id)s"
      product="%(product)s"
      factory="%(factory)s"
      condition="%(condition)s" />
"""

def addArchetypeContentRule(self,
                            id,
                            condition,
                            RESPONSE = None
                            ):
    """
    add an archetype rule
    """
    atrule = ArchetypeContentRule(id, condition)
    self._setObject(id, atrule)
    if RESPONSE is not None:
        return RESPONSE.redirect('manage_workspace')
    
addArchetypeContentRuleForm = DTMLFile('ui/ArchetypeContentRuleAddForm', globals())

class ArchetypeContentRule(SimpleItem):

    meta_type = "Archetype Content Rule"
    
    implements(IContentRule)

    security = ClassSecurityInfo()

    def __init__(self, id, condition):
        self.id = id
        self.condition = Expression( condition )
        self.condition_text = condition
        self.title = condition

    def isValid(self, content, context):
        if not isinstance( content, (atapi.BaseContent, atapi.BaseFolder) ):
            return False
        elif self.condition_text and not self.condition( context ):
            return False
        return True

    def process(self, descriptor, context):
        content = descriptor.getContent()
        resource_descriptors = self.getSchemaResources( content )
        child_descriptors = False
        for rd in resource_descriptors:
            descriptor.addChildDescriptor( rd )
            child_descriptors = True

        descriptor.setRenderMethod('view')
        if child_descriptors or descriptor.isContentFolderish():
            descriptor.setFileName( "%s/index.html"%content.getId() )
        else:
            descriptor.setFileName( self.getResourceName( content ) )

        descriptor.rule_id = self.getId()
            
        return descriptor

    def getSchemaResources( self, content):
        schema = content.Schema()
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
        cid = content.getId()
        if '.' in cid:
            return cid
        elif hasattr(content, 'content_type') and content.content_type:
            if callable(content.content_type):
                content_type = content.content_type()
            else:
                content_type = content.content_type
            major, minor = content_type.split('/')
            if major == 'text' and minor == 'plain':
                minor = 'html'
            if major == 'text' and minor == 'structured':
                minor = 'html'
            if major == 'text' and minor == 'x-rst':
                minor = 'html'
            return "%s.%s"%(cid, minor)
        raise RuntimeError("Could not Determine Extension")

    def toXml(self):
        d = {'id':self.id,
             'product':'ATContentRule',
             'factory':'addArchetypeContentRule',
             'condition':self.condition_text }

        return xml_export_template%d
    

InitializeClass(ArchetypeContentRule)

ContentSchema = atapi.BaseSchema + atapi.Schema((
    atapi.ImageField('portrait',
               mode='rw',
               accessor='getPortrait',
               mutator='setPortrait',
               max_size=(150,150),
               required=0,
               widget=atapi.ImageWidget(
                   label='Portrait',
                   label_msgid='label_portrait',
                   description="To add or change the portrait: click the "
                       "\"Browse\" button; select a picture of yourself. "
                       "Recommended image size is 75 pixels wide by 100 "
                       "pixels tall.",
                   description_msgid='help_portrait',
                   i18n_domain='plone',
                   ),
               ),
    ))


class SampleImageSchemaContent( atapi.BaseContent ):

    schema = ContentSchema
    archetype_name = portal_type = meta_type = "Sample Image Content"

atapi.registerType( SampleImageSchemaContent, PROJECT_NAME)


FolderSchema = atapi.BaseFolderSchema + atapi.Schema((
    atapi.ImageField('portrait',
               mode='rw',
               accessor='getPortrait',
               mutator='setPortrait',
               max_size=(150,150),
               required=0,
               widget=atapi.ImageWidget(
                   label='Portrait',
                   label_msgid='label_portrait',
                   description="To add or change the portrait: click the "
                       "\"Browse\" button; select a picture of yourself. "
                       "Recommended image size is 75 pixels wide by 100 "
                       "pixels tall.",
                   description_msgid='help_portrait',
                   i18n_domain='plone',
                   ),
               ),
    ))

class SampleImageSchemaFolder( atapi.BaseFolder ):

    schema = FolderSchema
    archetype_name = portal_type = meta_type = "Sample Image Folder"

atapi.registerType( SampleImageSchemaFolder, PROJECT_NAME)


def initialize(context):

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes( PROJECT_NAME ),
        PROJECT_NAME
        )

    utils.ContentInit(
        PROJECT_NAME + ' Content',
        content_types      = content_types,
        permission         = CMFCorePermissions.AddPortalContent,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    

    context.registerClass(
        ArchetypeContentRule,
        permission = 'Add Content Rule',
        constructors = ( addArchetypeContentRuleForm,
                         addArchetypeContentRule ),
        visibility = None
        )

