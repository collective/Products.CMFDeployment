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
Purpose: Data object to track a deployed content object
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: Descriptor.py 1238 2006-03-15 01:20:14Z hazmat $
"""

from Acquisition import aq_base

class DescriptorFactory:

    def __init__(self, ctx):
        self.ctx = ctx
        org  = ctx.getContentOrganization()
        self.is_composite = make_lookup(org.getActiveStructure().getCompositeDocumentTypes())

    def __call__(self, content):
        d = ContentDescriptor(content)
        d.content_url = content.absolute_url(relative=1)
        d.content_folderish_p = getattr(aq_base(content), 'isAnObjectManager', 0)
        d.composite_content_p = self.is_composite(content.getPortalTypeName())
        return d
        
def make_lookup(seq):
    d = {}
    for s in seq:
        d[s]=None
    return d.has_key
    

class DescriptorContainer(list):
    """
    container object for descriptors
    """

class ContentDescriptor(object):
    """
    a drop of water in a sieve
    """

    def __init__(self, content):
        self.content = content
        self.extension = None
        self.rendered  = None
        self.render_method = None
        self.binary = None
        self.ghost = None
        self.content_path = None
        self.source_path = None # relative path to content
        self.content_url = None
        self.content_folderish_p = None
        self.composite_content_p = None
        self.child_descriptors = None

        self.rule_id = None # id of rule that processed descriptor / matched content

        self.dependencies = None
        self.reverse_dependencies = None
        self.aliases = None
        
    def getId(self):
        return self.content.getId()

    def getDescriptors(self):
        descriptors = self.getChildDescriptors()
        if descriptors is None:
            return (self,)
        return (self,)+tuple(descriptors)

    def getAliases(self):
        return self.aliases or ()

    def getContent(self):
        return self.content

    def getRendered(self):
        return self.rendered

    def setRendered(self, rendered):
        self.rendered = rendered
        
    def getRenderMethod(self):
        return self.render_method 

    def setRenderMethod(self, method_name):
        self.render_method = method_name

    #################################
    # this is a misnomer it reflects the entire
    # portion of the last path segment ie foo.txt

    def getExtension(self):
        return self.extension

    def setExtension(self, extension):
        self.extension = extension

    setFileName = setExtension
    
    def getFileName(self):
        return self.extension
    #################################
    
    def getContentURL(self):
        return self.content_url

    def setContentURL(self, content_url):
        self.content_url = content_url

    def setContentFolderish(self, flag):
        self.content_folderish_p = flag
        
    def isContentFolderish(self):
        return not not self.content_folderish_p

    def setCompositeContent(self, flag):
        self.composite_content_p = not not flag

    def isCompositeContent(self):
        return self.composite_content_p
    
    def isGhost(self):
        return not not self.ghost

    def setGhost(self, flag):
        self.ghost = flag

    def isBinary(self):
        return not not self.binary

    def setBinary(self, flag):
        self.binary = flag

    def setContentPath(self, path):
        self.content_path = path

    def getContentPath(self):
        return self.content_path 

    def setSourcePath(self, path):
        self.source_path = path
        
    def getSourcePath(self):
        return self.source_path

    #################################
    # child resource management - for non portal content
    
    def addChildDescriptor(self, descriptor):
        if self.child_descriptors is None:
            self.child_descriptors = DescriptorContainer()
        self.child_descriptors.append( descriptor )
            
    def getChildDescriptors(self):
        return self.child_descriptors or ()

    def getContainedDescriptors(self, include_self=True):
        if include_self:
            yield self
        for d in self.getChildDescriptors():
            for s in d.getContainedDescriptors():
                yield s

    #################################
    # dependency management

    def getDependencies( self ):
        return self.dependencies or ()

    def setDependencies( self, dependencies ):
        self.dependencies = dependencies 

    def getReverseDependencies( self ):
        return self.reverse_dependencies or []

    def setReverseDependencies( self, reverse_dependencies ):
        self.reverse_dependencies = reverse_dependencies

