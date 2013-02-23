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
Purpose: Stores Rendered Content on the FileSystem
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id: storage.py 1237 2006-03-14 23:50:00Z hazmat $
"""

from core import Consumer

from Products.CMFDeployment.Log import LogFactory
#from Products.CMFDeployment.Statistics import IOStatistics

from Products.CMFDeployment.DefaultConfiguration import DEPLOYMENT_DEBUG

import os, itertools
from os import sep, path, mkdir
log = LogFactory('Content Storage')

class StorageManifest( object ):

    # XXX todo
    def __init__(self):
        self._items = []

    def add(self, path ):
        pass

    def remove( self, path ):
        pass


class ContentStorageManager(object):

    stats = None
    structure = None
    transforms = None
    
    def getStatistics(self):
        return self.stats

    def getStructure(self, pipe):
        if self.structure is None:
            self.structure = pipe.services['ContentOrganization'].getActiveStructure()
        return self.structure

    def getTransforms(self, pipe):
        if self.transforms is None:
            self.transforms = pipe.services["ContentTransforms"]
        return self.transforms

    def add(self, pipe, descriptor):
        """
        store a rendered content object on the filesystem.
        """
        # sometimes we want to have content in the uri db
        # but we don't actually want to store it... either because
        # of an error during rendering or based on configuration.
        if descriptor.isGhost(): 
            return 

        descriptors = descriptor.getContainedDescriptors()
        structure = self.getStructure( pipe )
        
        for descriptor in descriptors:
            if descriptor.isGhost(): # if a child view errors then it has no content
                continue
            content_path = structure.getContentPathFromDescriptor( descriptor )
            #if content_path.endswith(sep):
            #log.warning('invalid content path detected %s ... fixing'%content_path)
            #    content_path = content_path[:-1]
            try:
                self.storeDescriptor( pipe, content_path, descriptor )
            except:
                if not DEPLOYMENT_DEBUG:
                    raise
                import pdb, sys, traceback
                traceback.print_exc()
                pdb.post_mortem(sys.exc_info()[-1])

        return True
    
    def remove(self, pipe, descriptor):
        """
        remove a rendered content object on the filesystem
        """
        
        descriptors = descriptor.getContainedDescriptors()
        structure   = self.getStructure( pipe )

        for descriptor in descriptors:
            content_path = structure.getContentPathFromDescriptor( descriptor )
            file_name = descriptor.getFileName()
            location = path.join( content_path, file_name )
            #print "removing descriptor", file_name, location
            if path.exists( location ) and os.path.isfile( location ):
                os.remove( location )
            elif os.path.exists( location ):
                pass
                # removing directories is possible but requires a bit of work
                # as we map folder descriptors to index files..
                # basically need to store is_content_folderish on deletion descriptor
                # and chop of the last part of the location.. could be dangerous
                #print "Invalid - Directory Path", location, descriptor
            else: # already removed..
                pass
                
    def storeDescriptor(self, pipe, content_path, descriptor ):
        """
        """
        filename = descriptor.getFileName()
        location = path.join( content_path, filename )
        rendered = descriptor.getRendered()

        # creates directories as needed below mount point
        if not self.createParentDirectories( location ):
            return
            
#        self.stats( location, len(rendered) )
        rendered = self.getTransforms(pipe).transform(descriptor, rendered, location)
        if not rendered:
            return

        log.debug("storing content %s at %s"%(descriptor.content_url, location))

        if rendered is None:
            log.warning("no rendered content for %s at %s"%(descriptor.content_url, location))
            return

        fh = open(location, 'w')
        try:
            if isinstance( rendered, unicode ):
                rendered = rendered.encode('utf-8')
            fh.write(rendered)
        finally:
            fh.close()

    def createParentDirectories(self, location ):
        """
        creates parent directories as needed below mount point
        for the given location
        """
        directory = path.dirname( location )
        if path.exists( directory ):
            return True
        if not location.startswith( self.structure.mount_point ):
            log.warning( 'invalid store location %s'%(location))
            return False
        log.debug("creating parent directories for location %s"%location)
        components = directory.split(sep)
        for i in range( 2, len(components)+1 ):
            ppath = sep.join( components[:i] )
            if not path.exists( ppath ):
                mkdir( ppath )
        return True
                        
        
class ContentStorage( Consumer, ContentStorageManager ):

    process = ContentStorageManager.add

class ContentRemoval( Consumer, ContentStorageManager ):

    process = ContentStorageManager.remove            

