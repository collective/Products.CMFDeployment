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
Purpose: Stat Gathering for instrumentation
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: stats.py 1148 2006-01-31 07:31:01Z hazmat $
"""

from time import time, sleep
from cStringIO import StringIO
import unittest, sys

class IStatistics:

    def __call__(*arg, **kwarg):
        """
        implementation specific stat gathering
        """

    def stop():
        """
        signal end of stat collection
        """

    def pprint():
        """
        print stats
        """

class LogStatistics:
    pass

try:
    from linuxproc.linuxproc import self_statm
    from resource import getpagesize

    def zero():
        return 0
    
    class MemoryStatistics:

        def __init__(self):
            self._data = {}
            self._last_mem = self._get_memstat()

        def _get_memstat(self):
            return ( self_statm().get('size') * getpagesize()/1024,
                     getattr(sys, 'gettotalrefcount', zero)() )
        
        def __call__(self, name):
            lmem, lref = self._last_mem
            stat = self._get_memstat()
            mem, ref = self._data.setdefault(name, (0,0))
            mem += stat[0]-lmem
            ref += stat[1]-lref
            self._data[name]=(mem, ref)
            self._last_mem = stat
            
        def stop(self):
            pass

        def pprint(self):
            buf = StringIO()

            print >> buf, " Mem Stats Summary "
            print >> buf, ""
            for k,v in self._data.items():
                print >> buf, k, ":", v
            print >> buf, ""

            return buf.getvalue()

except:

    class MemoryStatistics:

        def __call__(self, *args): pass
        def stop(self): pass
        def pprint(self):
            return 'Mem Stats Unavailable'

class IOStatistics:

    __implements__ = IStatistics

    def __init__(self):
        self._total_bytes = 0
        self._files = {}

    def __call__(self, file_path, size):
        self._files[file_path]=size
        self._total_bytes += size
        
    def stop(self):
        pass

    def pprint(self, extra=0):
        buf = StringIO()

        print >> buf, " IO Stats Summary "
        print >> buf, ""
        print >> buf, "Total Transfer: %d"%self._total_bytes

        return buf.getvalue()

class TimeStatistics:

    __implements__ = IStatistics

    def __init__(self):

        self._stats = {}
        self._time_log = {}
        self._stime = time()
        self._etime = None
        self._last_time = self._stime
        #self._order = []

    def __call__(self, name, relative=0):

        ltime = time()
        if relative:
            diff = ltime - self._time_log[relative]
        else:
            diff  = ltime-self._last_time

        self._last_time = ltime
        self._time_log[name]=ltime
        
        if self._stats.has_key(name):
            self._stats[name] += diff
        else:
            self._stats[name] = diff

        #self._order.append(name)

    def stop(self):
        if self._etime is None:
            self._etime = time()

    def pprint(self, extra=0):

        if self._etime is None:
            return
        
        res = []
        buf = StringIO()

        print >> buf, "Time Statistics Summary"
        print >> buf, ""
        print >> buf, "%s%s"%("Total Time:".ljust(30), (self._etime-self._stime))
        
        if extra:
            print >> buf, "%s%s"%("Start Time:".ljust(30), str(self._stime))
            print >> buf, "%s%s"%("End Time:".ljust(30), str(self._etime))

        print >> buf, ""
        print >> buf, ""

        for s in self._stats.keys():
            print >> buf, "%s%s"%(s.ljust(35), str(self._stats[s]))

        return buf.getvalue()

    def getStartTime(self):
        return self._stime
    
    def getEndTime(self):
        return eslf._etime
        

class TimeStatTests(unittest.TestCase):
    # cheesy visual tests
    
    def testSimple(self):

        stats = TimeStatistics()
        stats('hello')
        stats.stop()
        print 'a', stats.pprint()
        
    def testAggregation(self):

        stats = TimeStatistics()
        stats('hello')
        stats('hello')
        stats('hello')
        sleep(1)
        stats('hello')
        stats('hello')        
        stats.stop()
        print 'b', stats.pprint()

    def testInterleavedAggregation(self):
        stats = TimeStatistics()

        stats('hello')
        sleep(1)
        stats('bye')
        stats('hello')
        sleep(1)
        stats('bye')
        stats('hello')
        stats.stop()
        print 'c', stats.pprint()

if __name__ == '__main__':
    unittest.main()
