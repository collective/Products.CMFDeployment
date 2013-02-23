##################################################################
#
# (C) Copyright 2002-2006 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: read an xml serialization of a deployment policy into python objects
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
$Id: reader.py 1249 2006-03-17 09:20:52Z hazmat $
"""

from xml.sax import make_parser, ContentHandler
from UserDict import UserDict

#from ZPublisher.mapply import mapply

marker = []
class PolicyNode(UserDict):
    reserved = ('data',)

    def __hasattr__(self, name):
        v = self.__dict__.get(name, marker)
        if v is marker:
            return self.data.has_key(name)
        return True

    def __getattr__(self, name):
        v = self.__dict__.get(name, marker)
        if v is marker:
            return self.data[name]
        return v
    
    def __setattr__(self, name, value):
        if name in PolicyNode.reserved:
            self.__dict__[name]=value
        else:
            self.data[name]=value
    
class MetaReader(ContentHandler):

    def __init__(self, parser, alt_element, alt_handler):

        self.parser = parser
        self.alt_element = alt_element
        self.alt_handler = alt_handler

        self.buf = []
        self.prefix = ''
        self.stack = []
        
    def startElement(self, element_name, attrs):
        name = element_name.lower()
        if name == self.alt_element:
            self.alt_handler.startElement( element_name, attrs )
            return self.parser.setContentHandler( self.alt_handler )

        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())      
        method = getattr(self, 'start%s'%name.capitalize(), None)

        # get rid of unicode
        d = {}
        for k, v in attrs.items():
            d[str(k)]= str(v)
        
        if method: 
            apply(method, (d,))

    def endElement(self, element_name):
        chars = str(''.join(self.buf)).strip()
        self.buf = []

        name = element_name.lower()
        
        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())            
        method = getattr(self, 'end%s'%name.capitalize(), None)
        
        if method: 
            apply(method, (chars,))
         
    def characters(self, chars):
        self.buf.append(chars)


class PolicyReader(MetaReader):

    def startDeploymentpolicy(self, attrs):
        self.policy = PolicyNode(attrs)

    def startIdentification(self, attrs):
        self.policy.ident = PolicyNode(attrs)
        self.prefix = 'Ident'

    def endIdentidentification(self, chars):
        self.prefix =''

    def startIdentsource(self, attrs):
        sources =  self.policy.ident.setdefault('sources', [] )
        source = PolicyNode( attrs )
        sources.append( source )
        
    def startIdentfilter(self, attrs):
        filters = self.policy.ident.setdefault('filters', [])
        filter = PolicyNode(attrs)
        filters.append(filter)

    def startOrganization(self, attrs):
        organization = PolicyNode(attrs)
        organization['restricted']=[]
        self.policy.organization = organization
        self.prefix='Organization'

    def startOrganizationrestricted(self, attrs):
        restricteds = self.policy.organization.setdefault('restricted', [])
        restricteds.append(attrs['id'])

    def startOrganizationcomposite(self, attrs):
        composites = self.policy.organization.setdefault('composites', [])
        composites.append(attrs['type'])

    def endOrganizationorganization(self, chars):
        self.prefix=''
        
    def startMastering(self, attrs):
        mastering = PolicyNode(attrs)
        self.policy.mastering = mastering
        self.prefix='Mastering'

    def endMasteringmastering(self, chars):
        self.prefix=''
        
    def startMasteringmime(self, attrs):
        mimes = self.policy.mastering.setdefault('mimes', [])
        mime = PolicyNode(attrs)
        if mime.has_key('ghost'):
            mime['ghost'] = int(mime.ghost)
        mimes.append(mime)

    startMasteringrule = startMasteringmime

    def startSkins(self, attrs):
	skins = PolicyNode(attrs)
	self.policy.skins = skins
	self.prefix='Skins'
        self.policy.skins.setdefault('directories',[])

    def startSkinsdirectory(self, attrs):
	dirs = self.policy.skins.setdefault('directories', [])
	sd = PolicyNode(attrs)
	dirs.append(sd)

    def endSkinsskins(self,attrs):
	self.prefix=''

    def startResources(self, attrs):
        resources = PolicyNode( attrs )
	self.policy.resources = resources
	self.prefix='Resources'
        self.policy.resources.setdefault('resources',[])        

    def startResourcesresource(self, attrs):
	resources = self.policy.resources.setdefault('resources', [])
	resource = PolicyNode(attrs)
	resources.append(resource)

    def endResourcesresources(self,attrs):
	self.prefix=''

    def startRegistries(self, attrs):
	registries = PolicyNode(attrs)
	self.policy.registries = registries
	self.prefix='Registries'
        self.policy.registries.setdefault('registries',[])

    def startRegistriesregistry(self, attrs):
	dirs = self.policy.registries.setdefault('registries', [])
	reg = PolicyNode(attrs)
	dirs.append(reg)

    def endRegistriesregistries(self,attrs):
	self.prefix=''


#    def startStrategy(self, attrs):
#        self.policy.strategy = PolicyNode(attrs)

    def startUris(self, attrs):
        self.policy.uris = PolicyNode(attrs)

    def startChain_user(self, attrs):
        self.policy.chain_user = PolicyNode(attrs)
	
    def getPolicy(self):
        return self.policy
        
def read_policy(file):
    # file = file handle
    parser = make_parser()
    reader = PolicyReader()
    parser.setContentHandler(reader)
    parser.parse(file)
    return reader.getPolicy()

REMAP_TYPES = ( ( 'CMFDeployment', 'addContentRule' ),
                ( 'CMFDeployment', 'addMimeMapping' ),
                ( 'CMFDeployment', 'addATContainerRule' ),
                ( 'CMFDeployment', 'addATContentRule'),
                ( 'CMFDeployment', 'addATCompositeRule') )
                
                

DEFAULT_RULE_PRODUCT = 'CMFDeployment'    
DEFAULT_RULE_FACTORY = 'addContentRule'
DEFAULT_RULE_FACTORY_MAP = {
    'ext_expr':'extension_expression',
    'filter_expr':'condition'
    }

DEFAULTS = {
    'source' : {'product':'CMFDeployment', 'factory':'addPortalCatalogSource' },
    }

def remap_default_rule_factory( m ):
    delk = []
    for key, factory_key in DEFAULT_RULE_FACTORY_MAP.items():
        if factory_key in m:
            continue
        value = m.get(key, '')
        m[factory_key] = value
        if key in m:
            delk.append(key)

    for dk in delk:
        if dk in m:
            del m.data[dk]

    return m

def getFactory( ctx, node, type='source' ):
    product_name = node.get('product', DEFAULTS[type]['product'])
    factory_name = node.get('factory', DEFAULTS[type]['factory'])
    factory = getattr( ctx.manage_addProduct[ product_name ], factory_name )
    md = dict( node )
    if 'product' in md: del md['product']
    if 'factory' in md: del md['factory']
    return factory, md
    

def make_policy(portal, policy_node, id=None, title=None):
 
    import DefaultConfiguration
    from App.Common import package_home

    deployment_tool = portal.portal_deployment

    pipeline_id = policy_node.get('pipeline', 'incremental')
    
    if id:
        title = title or ''
    else:
        id = policy_node.id

    deployment_tool.addPolicy( id, title, policy_pipeline_id=pipeline_id )
        
    policy = getattr(deployment_tool, id)
    
    identification = getattr(policy, DefaultConfiguration.ContentIdentification)
    if hasattr(policy_node.ident, 'filters'):
        for f in policy_node.ident.filters:
            identification.filters.addFilter(f.id, f.expr)

    if hasattr(policy_node.ident, 'sources'):
        container = identification.sources
        for s in policy_node.ident.sources:
            factory, md = getFactory( container, s )
            factory( **md )

    ## mastering setup
    mastering = getattr(policy, DefaultConfiguration.ContentMastering)    
    
    for m in policy_node.mastering.mimes:
        # transparently map old policies to the expected format
        product = m.get('product', DEFAULT_RULE_PRODUCT)
        factory = m.get('factory', DEFAULT_RULE_FACTORY)
        #import pprint
        #print 'ee', product, factory
        #pprint.pprint(dict(m.items()))

        if (product, factory) in REMAP_TYPES:
            #print 'remapped'
            m.setdefault('ghost',0)
            m = remap_default_rule_factory( m )

        #pprint.pprint( dict( m.items() ) )
            
        factory = getattr(mastering.rules.manage_addProduct[product], factory)
        md = dict(m)
        if 'product' in md: del md['product']
        if 'factory' in md: del md['factory']
        factory( **md )
        #mapply(factory, keyword=m)
        
    ## chain stuff
    deployment_skin = policy_node.mastering.skin.strip()
    
    if deployment_skin:
        mastering.editSkin(enable=1, skin_name=deployment_skin)

    if policy_node.has_key('chain_user'):
        mastering.site_user.edit(enable=1,
                                 user=policy_node.chain_user.user,
                                 udb_path=policy_node.chain_user.udb_path)        

    ## org setup
    organization = getattr(policy, DefaultConfiguration.ContentOrganization)

    fs_mount = policy_node.organization.fs_mount
    
    if fs_mount.startswith('*'): # a little trick for the example
        cmfdeploydir = package_home(globals())
        fs_mount = fs_mount.replace('*', cmfdeploydir)
        
    organization.structure.setMountPoint(fs_mount)
    organization.structure.setCMFMountPoint(policy_node.organization.cmf_mount)
    
    if policy_node.organization.has_key('restricted'):
        organization.structure.setRestrictedPoints(policy_node.organization.restricted)

    if policy_node.organization.has_key('composites'):
        organization.structure.setCompositeDocumentTypes(policy_node.organization.composites, _force=1)        

    ## uris setup
    uris = getattr(policy, DefaultConfiguration.ContentURIs)

    if policy_node.has_key('uris'):
        if policy_node.uris.has_key('target_path'):
            uris.editContentURI(target_path=policy_node.uris.target_path,
                                vhost_path=policy_node.uris.vhost_path,
                                link_error_url=policy_node.uris.link_errors
                                )

    #################################
    # Site Resources setup

    # backwards compat skin directory
    resources = getattr( policy, DefaultConfiguration.SiteResources )

    if hasattr( policy_node, 'skins') and hasattr( policy_node.skins, 'directories'):
        for sd in policy_node.skins.directories:
            id = sd.get('id', sd.view_path.replace('/',''))
            resources.manage_addProduct['CMFDeployment'].addDirectoryViewRule(
                id,
                sd.view_path, 
                sd.source_path, 
                sd.deploy_path
                )
            
    ## backwards compat registry rule
    if hasattr( policy_node, 'registries') and hasattr( policy_node.registries, 'registries'):
        for reg in policy_node.registries.registries:
            id = reg.get('id', reg.view_path.replace('/',''))
            if not id.startswith('reg_'):
                id = "reg_" + id
            resources.manage_addProduct['CMFDeployment'].addResourceRegistryRule(
                id,
                reg.view_path, 
                reg.source_path, 
                reg.deploy_path
                )

    # new style resource specification
    if hasattr(policy_node, 'resources') and hasattr(policy_node.resources, 'resources'):
        for resource_node in policy_node.resources.resources:
            factory, md = getFactory( resources, resource_node )
            factory( **md )
  
    # strategy setup - XXX convert to pipeline id
#    strategies = getattr(policy, DefaultConfiguration.DeploymentStrategy)
#    if policy_node.has_key('strategy') and policy_node.strategy.has_key('id'):
#        strategies.setStrategy(policy_node.strategy.id)

    return policy
    
if __name__=='__main__':

    import sys
    import pprint
    
    policy = read_policy(sys.argv[1])

    for k,v in policy.items():
        print k
        
        for k,v in v.items():
            print "  "*5, k, v
        
    
