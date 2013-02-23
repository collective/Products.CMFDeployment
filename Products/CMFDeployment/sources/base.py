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
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: base.py 1205 2006-03-04 23:04:46Z hazmat $
"""

from Products.CMFDeployment.utils import SerializablePlugin
from Products.CMFDeployment.Namespace import getToolByName

source_template = """\
 <source id="%(id)s"
         title="%(title)s"
         product="%(product)s"
         factory="%(factory)s" />
"""         

class BaseSource( SerializablePlugin ):

    meta_type = 'Base Source'
    xml_template = source_template
    xml_factory  = ""

    icon_path = 'folder_icon.gif'

    # zmi icon
    def icon(self):
        return getToolByName(self, 'portal_url')(relative=1)+'/'+self.icon_path
    
