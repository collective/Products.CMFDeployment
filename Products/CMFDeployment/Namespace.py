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
Purpose: Normalize import of common jaunx
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: Namespace.py 1990 2007-07-12 15:09:19Z hazmat $
"""


from AccessControl import ClassSecurityInfo, Permissions, getSecurityManager
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
import App.Undo
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime
from App.special_dtml import DTMLFile
from AccessControl.class_init import InitializeClass
from App.Common import package_home
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.OrderedFolder import OrderedFolder
from OFS.ObjectManager import ObjectManager, IFAwareObjectManager
from Products.CMFCore.utils import UniqueObject, SimpleItemWithProperties, getToolByName

try:
    from Products.CMFCore import CMFCorePermissions
except ImportError:
    from Products.CMFCore import permissions as CMFCorePermissions

from zope.interface import Interface
from ZODB.PersistentMapping import PersistentMapping
