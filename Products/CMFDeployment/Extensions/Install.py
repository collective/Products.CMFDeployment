
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment import DeploymentTool
from Products.CMFCore.DirectoryView import addDirectoryViews


def uninstall( self ):
    out = StringIO()
    skinstool = getToolByName(self, 'portal_skins')

    # get rid of deployment skin
    skins = skinstool.getSkinSelections()
    skinstool.manage_skinLayers( chosen=('Plone Deployment',),
                                 del_skin=True )

    # get rid of skin directories
    skinstool.manage_delObjects( ['deployment_templates'] )

    # delete policies, they clean up after themselves
    self.portal_deployment.manage_delObjects( self.portal_deployment.objectIds() ) 
        
    # get rid of deployment tool itself
    self.portal_url.getPortalObject().manage_delObjects( DeploymentTool.DeploymentTool.id )

    # get rid of catalog index
    self.portal_catalog.manage_deleteIndex( ('content_modification_date',)  )
    
def install(self):
    out = StringIO()
    skinstool = getToolByName(self, 'portal_skins')

    ob = DeploymentTool.DeploymentTool()
    self._setObject(ob.getId(), ob)

    if 'deployment_templates' not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', DeploymentProductHome)
        out.write("Added 'deployment_templates' directory view to portal_skins\n")

    # dont install deployment skin in 2.1
    if True:
    #if self._getOb('portal_css', None) is None:
        skins = skinstool.getSkinSelections()
        if 'Plone Deployment' not in skins:
            path=[elem.strip() for elem in \
                  skinstool.getSkinPath('Plone Default').split(',')]
            path.insert(path.index('custom')+1, 'deployment_templates')
            skinstool.addSkinSelection('Plone Deployment', ','.join(path))
        else:
            out.write("Plone Deployment skin already setup\n")

    if 'content_modification_date' not in self.portal_catalog.indexes():
        self.portal_catalog.manage_addIndex( "content_modification_date", "FieldIndex")

    portal = self.portal_url.getPortalObject()
    portal.portal_catalog.indexObject( portal )

    return out.getvalue()
