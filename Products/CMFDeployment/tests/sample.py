from Products.Archetypes import public as atapi
from Products.CMFCore.TypesTool import FactoryTypeInformation

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

atapi.registerType( SampleImageSchemaContent, "CMFDeployment")

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

atapi.registerType( SampleImageSchemaFolder, "CMFDeployment")

def registerContent( portal ):

    # add type information for Dummy
    tt = portal.portal_types
    tt.manage_addTypeInformation(
        FactoryTypeInformation.meta_type,
        id = 'Simple Image Folder',
        typeinfo_name = 'CMFDefault: Skinned Folder')

    tt.manage_addTypeInformation(
        FactoryTypeInformation.meta_type,
        id = 'Simple Image Content',
        typeinfo_name = 'CMFDefault: Document')    
