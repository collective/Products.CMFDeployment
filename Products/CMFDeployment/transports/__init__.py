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
Purpose: Transfer Deployed Content to Deployment Server
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 9/10/2002
$Id: __init__.py 1397 2006-06-26 06:15:44Z hazmat $
"""
# deployment protocol implementation directory

from Products.CMFDeployment.Log import LogFactory


log = LogFactory("Transports")

try:
    import rsync
except ImportError:
    log.error("rsync not available")
    rsync = None

try:
    import sitecopy
except ImportError:
    log.error("sitecopy not available")
    sitecopy = None

try:
    import ziptransport
except ImportError:
    log.error("ziptransport not available")
    ziptransport = None

#################################
# simple global protocol registry    

## class ProtocolDatabase:

##     def __init__(self):
##         self._protocols = {}

##     def registerProtocol(self, name, protocol):
##         self._protocols[name]=protocol

##     def getProtocolNames(self, context=None):
##         return self._protocols.keys()

##     def getProtocol(self, name):
##         return self._protocols[name]

## _protocols = ProtocolDatabase()

## registerProtocol = _protocols.registerProtocol
## getProtocolNames = _protocols.getProtocolNames
## getProtocol = _protocols.getProtocol


## #################################
## # protocol implementation

## from rsync import RsyncSshProtocol
## registerProtocol('rsync_ssh', RsyncSshProtocol())

