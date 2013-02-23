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

Purpose: Simple History storage... to be expanded
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
$Id: DeploymentHistory.py 1661 2006-09-14 02:38:47Z hazmat $

"""
from Namespace import *
from BTrees.OIBTree import OISet
from BTrees.IOBTree import IOBTree
from BTrees.Length import Length
from Log import getMonitors

class DeploymentHistoryContainer(Folder):

    all_meta_types = ()
    
    meta_type = 'Deployment History Container'

    manage_options = (
        
        {'label':'History',
         'action':'history_overview'},

        {'label':'Policy',
         'action':'../overview'},
        )

    security = ClassSecurityInfo()

    history_overview = DTMLFile('ui/DeploymentHistoryOverview', globals())

    def __init__(self, id):
        self.id = id
        self._records = IOBTree() # OISet()
        self._record_length = Length(0)

    #security.declarePrivate('addHistory')
    #def addHistory(self):
    #    h = DeploymentHistory( str(self._record_length()) )
    #    self._records.insert(h)
    #    self._record_length.change(1)
    #    return h

    security.declarePrivate('attachHistory')
    def attachHistory(self, history):
        rid  = self._record_length()
        hid = str( rid )
        history.id = hid
        self._records[rid] = history
        self._record_length.change(1)
        
    security.declareProtected(Permissions.view_management_screens, 'getHistories')
    def getHistories(self):
        return tuple(self._records.values())

    security.declarePrivate('getLastTime')
    def getLastTime(self):
        if self._record_length() == 0:
            return None
        return self._records[ self._records.maxKey() ].creation_time

    def getLast(self):
        if self._record_length() == 0:
            return None
        return self._records[ self._records.maxKey() ].__of__(self)

    def getCurrent(self):
        # if called during deployment execution with an attached history
        monitors = getMonitors()
        # only one monitor.. need another tls? not used by anything else atm
        history = monitors.pop()
        return history

    security.declarePrivate('makeHistory')
    def makeHistory(self):
        return DeploymentHistory('Not Recorded')#.__of__(self)

    security.declarePrivate('clear')
    def clear(self):
        self._record_length = Length(0)
        self._records = IOBTree()
        
    def __bobo_traverse__(self, REQUEST, name=None):

        try:
            hid = int(name)
            return self._records[hid].__of__(self)
        except:
            return getattr(self, name)

InitializeClass(DeploymentHistoryContainer)

class DeploymentHistory(SimpleItem):

    meta_type = 'Deployment History'

    manage_options = ()

    security = ClassSecurityInfo()    

    index_html = DTMLFile('ui/HistoryView', globals())
    
    def __init__(self, id):
        self.id = id
        self.creation_time = DateTime()-2/(24*60*60)
        self.timeTime = str(int(self.creation_time.timeTime()))
        self.logs = []
        self.statistics = None
        
    def recordStatistics(self, stats_display):
        self.statistics = stats_display

    def log(self, msg, level):
        self.logs.append(msg)

    security.declarePublic('row_display')
    def row_display(self):
        
        return 'Deployed %s (<a href="%s">More Info</a>)'%(
            self.creation_time.fCommonZ(),
            self.id
            )

InitializeClass(DeploymentHistory)

    
