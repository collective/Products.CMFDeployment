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
Ripped From Gideon

Description:

  Provides an abstraction to the underlying logging
  framework.

Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
$Id: Log.py 1234 2006-03-14 08:46:36Z hazmat $
"""

from zLOG import LOG
from threading import Lock
from thread import get_ident
import DefaultConfiguration

APP_NAME = '[Deployment]'

_registered_components = {}
_monitors = {}
monitor_lock = Lock()

# in truly exceptional circumstances
# we don't care about the configuration
# we want to tell someone
OVERRIDE_THRESHOLD_LEVEL = 200

class ComponentLogging:

    def __init__(self, app_name, component_name):
        self._app = app_name
        self._component = component_name

    def compose(self, msg, extra, **kwargs):        
        return "[%s] : %s "%(self._component, msg)

    def write(self, msg, level):
        #if not DefaultConfiguration.DEPLOYMENT_DEBUG:
        #    return
        #print msg
        record_p, zlog_p = configuration.getConfigurationFor(self._component)
        if record_p or level >= OVERRIDE_THRESHOLD_LEVEL:
            monitors = getMonitors()
            for m in monitors:
                m.log(msg, level)

        if zlog_p or level >= OVERRIDE_THRESHOLD_LEVEL:
            LOG(self._app,
                level,
                msg,
                '')
        
    def debug(self, msg, extra='', **kwargs):
        self.write(self.compose(msg, extra, **kwargs), -100)

    def info(self, msg, extra='', **kwargs):
        self.write(self.compose(msg, extra, **kwargs), 0)        

    def warning(self, msg, extra='', **kwargs):
        self.write(self.compose(msg, extra, **kwargs), 100)

    def error(self, msg, extra='', **kwargs):
        self.write(self.compose(msg, extra, **kwargs), 200)
        
    def panic(self, msg, extra='', **kwargs):
        self.write(self.compose(msg, extra, **kwargs), 300)

def LogFactory(component_name):
    return ComponentLogging(APP_NAME, component_name)

class LogConfiguration:

    default=(1,1) # default is to record and log

    def __init__(self):
        self._components = {}

    def setConfigurationEntry(self, component_name, record=0, zlog=0):
        component_name = str(component_name)
        record = int(record)
        zlog = int(zlog)        
        self._components[component_name] = (record, zlog)

    def getConfigurationFor(self, component_name):
        return self._components.setdefault(component_name, self.default)
    
    def getConfigurationEntries(self):
        return self._components.items()

configuration = LogConfiguration()
getRegisteredComponents = _registered_components.keys

def getMonitors():
    tid = get_ident()
    return  _monitors.setdefault(tid, [])

def attachLogMonitor(monitor):
    tid = get_ident()
    monitor_lock.acquire()
    try:
        tmonitors = _monitors.setdefault(tid, [])
        tmonitors.append(monitor)
    finally:
        monitor_lock.release()
    
def detachLogMonitor(monitor):
    tid = get_ident()
    monitor_lock.acquire()
    try:        
        tmonitors = _monitors.get(tid, [])
        if monitor in tmonitors:
            tmonitors.remove(monitor)
    finally:
        monitor_lock.release()
