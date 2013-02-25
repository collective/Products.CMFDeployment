##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
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
Purpose: Initialize and Register the Deployment Tool
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id: __init__.py 1990 2007-07-12 15:09:19Z hazmat $
"""


import utils
from App.Common import package_home
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

from Namespace import CMFCorePermissions

DeploymentProductHome = package_home( globals() )

import DeploymentTool

tools = (DeploymentTool.DeploymentTool,)

import ContentOrganization
import ContentMastering
import ContentDeployment
import ContentIdentification
#import DeploymentStrategy
import Descriptor
import ContentRules

import resources
import rules
import transports
import sources
import incremental
import pipeline
import utils



registerDirectory('skins', globals())

methods = {
    'DeploymentPipelineIds':pipeline.getPipelineNames,
    'content_modification_date':utils.ContentModificationInspector()
    }

def initialize(context):

    ToolInit('CMF Deployment',
             tools=tools,
             product_name='Products.CMFDeployment',
             icon='tool.png').initialize(context)

    utils.registerIcon('policy.png')
    utils.registerIcon('identify.png')
    utils.registerIcon('protocol.png')     
    utils.registerIcon('resource_directory_view.gif')
    utils.registerIcon('resource_registry.gif')    
    
    # register default plugin components
    if transports.rsync is not None:
        
        rsync = transports.rsync
        context.registerClass(
            rsync.RsyncSSHTransport,
            permission = 'CMFDeploy: Add Deployment Transport',
            constructors = ( rsync.addRsyncSSHTransportForm,
                             rsync.addRsyncSSHTransport ),
            visibility = None
            )

    if transports.sitecopy is not None:
        sitecopy = transports.sitecopy
        context.registerClass(
            sitecopy.SiteCopyTransport,
            permission = 'CMFDeploy: Add Deployment Transport',
            constructors = ( sitecopy.addSiteCopyTransportForm,
                             sitecopy.addSiteCopyTransport ),
            visibility = None        
            )

    crule = rules.default
    context.registerClass(
        crule.ContentRule,
        permission = 'CMFDeploy: Add Content Rule',
        constructors = ( crule.addContentRuleForm,
                         crule.addContentRule ),
        visibility = None
        )

    atcontainer = rules.atcontainer
    context.registerClass(
        atcontainer.ATContainerRule,
        permission = 'CMFDeploy: Add Content Rule',
        constructors = ( atcontainer.addATContainerRuleForm,
                         atcontainer.addATContainerRule ),
        visibility = None
        )    

    atrule = rules.atcontent
    context.registerClass(
        atrule.ArchetypeContentRule,
        permission = 'CMFDeploy: Add Content Rule',
        constructors = ( atrule.addATContentRuleForm,
                         atrule.addATContentRule ),
        visibility = None
        )

    dview = resources.directoryview
    context.registerClass(
        dview.DirectoryViewRule,
        permission = CMFCorePermissions.ManagePortal,
        constructors = ( dview.addDirectoryViewRuleForm,
                         dview.addDirectoryViewRule ),
        visibility = None
        )

    registry = resources.registry
    context.registerClass(
        registry.ResourceRegistryRule,
        permission = CMFCorePermissions.ManagePortal,
        constructors = ( registry.addResourceRegistryRuleForm,
                         registry.addResourceRegistryRule ),
        visibility = None
        )

    rskin = resources.skin
    context.registerClass(
        rskin.SiteSkinResourceRule,
        permission = CMFCorePermissions.ManagePortal,
        constructors = ( rskin.addSkinResourceRuleForm,
                         rskin.addSkinResourceRule ),
        visibility = None
        )

    template = resources.template
    context.registerClass(
        template.ResourceTemplateRule,
        permission = CMFCorePermissions.ManagePortal,
        constructors = ( template.addResourceTemplateRuleForm,
                         template.addResourceTemplateRule ),
        visibility = None
        )

##     author = resources.author
##     context.registerClass(
##         author.AuthorIndexesRule,
##         permission = CMFCorePermissions.ManagePortal,
##         constructors = ( author.addAuthorIndexesRuleForm,
##                          author.addAuthorIndexesRule ),
##         visibility = None
##         )
    
    catalog = sources.catalog
    context.registerClass(
        catalog.PortalCatalogSource,
        permission = 'CMFDeploy: Add Content Source',
        constructors = ( catalog.addPortalCatalogSourceForm,
                         catalog.addPortalCatalogSource, ),
        visibility = None
        )

    context.registerClass(
        catalog.IncrementalCatalogSource,
        permission = 'CMFDeploy: Add Content Source',        
        constructors = ( catalog.addIncrementalCatalogSourceForm,
                         catalog.addIncrementalCatalogSource, ),
        visibility = None
        )
        
#    dependency = sources.dependency
#    context.registerClass(
#        dependency.DependencySource,
#        permission = 'CMFDeploy: Add Content Source',
#        constructors= (dependency.addDependencySourceForm,
#                       dependency.addDependencySource, ),
#        visibility = None
#        )

#    deletion = sources.deletion
#    context.registerClass(
#        deletion.DeletionSource,
#        permission = 'CMFDeploy: Add Content Source',
#        constructors= (deletion.addDeletionSourceForm,
#                       deletion.addDeletionSource, ),
#        visibility = None
#        )


    if sources.topic is not None:
        topic = sources.topic
        context.registerClass(
            topic.TopicSource,
            permission = 'CMFDeploy: Add Content Source',
            constructors= (topic.addTopicSourceForm,
                           topic.addTopicSource, ),
            visibility = None
            )    

    context.registerClass(
        incremental.PolicyIncrementalIndex,
        permission = 'Add Pluggable Index',
        constructors = (incremental.addPolicyIncrementalIndexForm,),
        icon='www/index.gif',
        visibility=None
        )    
