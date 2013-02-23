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
Purpose: Defines Exceptions for the Deployment Tool System
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: DeploymentExceptions.py 1248 2006-03-17 09:03:25Z hazmat $
"""

class CredentialError(Exception): pass
class ProtocolError(Exception): pass
class InvalidSkinName(Exception): pass
class InvalidCMFMountPoint(Exception): pass
class InvalidDirectoryView(Exception): pass
class InvalidResource(Exception): pass
class InvalidRegistry(Exception): pass
class InvalidPortalType(Exception): pass
