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
Purpose: File System Directory Proxies and Modeling
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: structure.py 1168 2006-02-18 03:43:43Z hazmat $
"""

import os
from Acquisition import aq_base
from OFS.ObjectManager import ObjectManager
from OFS.Folder import Folder

#from Interface import Base as Interface
from zope.interface import Interface

from Globals import DTMLFile

class DirectoryCreationException(Exception): pass

class IDirectory(Interface):

    """
    also implements IPropertyManager
    """

    def addDirectory(directory_name):
        """
        adds a sub directory to this
        directory with the given name
        """

    def getName():
        """
        returns the name of this directory
        """

    def getPath():
        """
        returns the absolute path of
        the directory relative to the
        root directory
        """

class IRootDirectory(IDirectory):

    def getRootDirectory():
        """
        return the root directory
        """

    def getDirectories():
        """
        returns a list consisting of this
        directory and all its sub directories
        """

    def getDirectoryPaths():
        """
        returns a list consisting of this
        directory and all its sub directory
        paths
        """

    def mountFileStructure(path):
        """
        creates a fascimile consisting of the
        file directory structure relative to this
        RootDirectory at path.
        """

class Directory(ObjectManager):

    meta_type = 'FS Structure Directory'

    def __init__(self, id):
        self.id = id

    def getName(self):
        return self.id

    getId = getName

    def getPath(self):
        directories = ascendant_obj_collector(self, "getRootDirectory")
        directories.reverse()
        return os.sep.join([d.getName() for d in directories])

    def addDirectory(self, directory_name):
        d = Directory(directory_name)
        self._setObject(directory_name, d, set_owner=0)

    def all_meta_types(self):
        return self.getRootDirectory().all_meta_types

class FileSystemMountError(Exception): pass

class FileSystemMountPoint:

    mount_point = None

    filesystem_mount = DTMLFile('ui/FileSystemMountForm', globals())
    
    def setMountPoint(self, mount_point, RESPONSE=None):
        """ """
        if not self.isValidMountPoint(mount_point):
            raise FileSystemMountError(" invalid mount point %s"%mount_point)
        self.mount_point = mount_point

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def isValidMountPoint(self, mount_point):
        checks = (os.F_OK, os.R_OK, os.W_OK, os.X_OK)
        return not not filter(None, map(lambda c, mp=mount_point, a=os.access: a(mp,c), checks))

    def getMountPoint(self):
        return self.mount_point

    def mount(self):
        directories = self.getDirectories()

        mp = self.mount_point
        j  = os.path.join
        e  = os.path.exists
        id = os.path.isdir
        md = os.mkdir
        
        paths = [d.getPath() for d in directories]
        for p in paths:
            dp = j(mp, p)
            if e(dp):
                if not id(dp):                
                    raise FileSystemMountError("file blocking mount %s"%dp)
                continue
            md(dp)
            
class RootDirectory(Folder, Directory, FileSystemMountPoint):

    meta_type = 'FS Structure Root'

    addDirectoryForm = DTMLFile('ui/StructureAddDirectoryForm', globals())

    all_meta_types = (
        {'name':Directory.meta_type,
         'action':'addDirectoryForm'},
        )

    def getName(self):
        return self.mount_point

    def getRootDirectory(self):
        return self

    def getDirectories(self):
        return descendant_obj_collector(self)

    def getDirectoryPaths(self):
        return [d.getPath() for d in self.getDirectories()]

#################################
# some variations on a theme     

def ascendant_obj_collector(obj, attribute_name):
    """
    collect objects up the containment hierarchy
    till we find one with an attribute_name attribute
    """

    res = []
    w = res.append
    o = obj.aq_inner

    while not hasattr(o.aq_base, attribute_name):
        w(o)
        o = o.aq_parent
    w(o)

    return res

class descender:

    def __init__(self, gc_threshold=100):
        self.gc_threshold = gc_threshold
        self.obj_count = 0

def descendant_obj_collector(o):
    """
    collect objects down the containment hierarchy
    """
    
    r = []
    for oc in o.objectValues():
        r.append(oc)
        if hasattr(oc.aq_base, 'isAnObjectManager'):
            r.extend(descendant_obj_collector(oc))
        if getattr(oc, '_p_changed', None)==None:
            if hasattr(oc, '_p_deactivate'):
                oc._p_deactivate()
    return r

def descendant_folder_collector(o):
    r = []
    w = r.append
    for oc in o.objectValues():
        if hasattr(aq_base(oc), 'isAnObjectManager'):
            w(oc)
            r.extend(descendant_folder_collector(oc))
        elif getattr(oc, '_p_changed', None)==None:
            if hasattr(oc, '_p_deactivate'):            
                oc._p_deactivate()
    return r

class descendant_filtered_folder_collector(descender):
    
    def __call__(self, o, filter):
        r = []
        w = r.append
        for oc in o.objectValues():
            self.obj_count += 1            
            if hasattr(aq_base(oc), 'isAnObjectManager'):
                if not filter(oc): continue
                w(oc)
                r.extend(self(oc, filter))
            elif getattr(oc, '_p_changed', None)==None:
                if hasattr(oc, '_p_deactivate'):            
                    oc._p_deactivate()
            if self.obj_count % self.gc_threshold == 0:
                if hasattr(o, '_p_jar'):
                    o._p_jar.cacheGC()
        return r

def descendant_filter_collector(o, filter):
    """
    with filter
    """
    r = []
    c = o.objectValues()
    r.extend(filter(None, map(filter, c)))
    
    for oc in c:
        if hasattr(oc.aq_base, 'isAnObjectManager'):
            r.extend(descendant_filter_collector(oc, filter))    
        if getattr(oc, '_p_changed', None)==None:
            oc._p_deactivate()
    
    return r 
