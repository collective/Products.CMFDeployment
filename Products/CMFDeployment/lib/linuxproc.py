##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
""" module for investigating the Linux /proc filesystem

"""
import os, re, string
__version__ = '1.0'

DIGITS = {}
for d  in "1234567890":
    DIGITS[d] = 1

# linux 2_2_18 /proc/self/stat format
l2_2_18_procstat = [
    'pid', 'comm', 'state', 'ppid', 'pgrp', 'session', 'tty', 'tty_pgrp',
    'flags', 'min_flt', 'cmin_flt', 'maj_flt', 'cmaj_flt', 'utime',
    'stime', 'cutime', 'cstime', 'priority', 'nice', 'NULL',
    'it_real_value', 'start_time', 'vsize', 'rss', 'rlim', 'start_code',
    'end_code', 'start_stack', 'esp', 'eip', 'signal',
    'blocked', 'sigign', 'sigcatch', 'wchan', 'nswap', 'cnswap',
    'exit_signal', 'processor'
    ]

# linux 2_2_18 /proc/loadavg format
l2_2_18_loadavg = ['1min', '5min', '15min', 'running', 'cumulative']

# linux 2_2_18 /proc/uptime format
l2_2_18_uptime = ['uptime', 'idle']

# linux 2_2_18 /proc/self/statm format
l2_2_18_procstatm = ['size', 'resident', 'shared', 'trs', 'drs', 'lrs', 'dt']

# linix 2_2_18 /proc/stat format
l2_2_18_stat = {
    'cpu'       : ['user', 'nice', 'system', 'idle'],
    'disk'      : ['unknown1', 'unknown2', 'unknown3'],
    'disk_rio'  : ['unknown1', 'unknown2', 'unknown3'],
    'disk_wio'  : ['unknown1', 'unknown2', 'unknown3'],
    'disk_rblk' : ['unknown1', 'unknown2', 'unknown3'],
    'disk_wblk' : ['unknown1', 'unknown2', 'unknown3'],
    'page'      : ['in', 'out'],
    'swap'      : ['in', 'out'],
    'intr'      : ['interrupts'],
    'ctxt'      : ['context_switches'],
    'btime'     : ['boot_time'],
    'processes' : ['processes'],
    }

# Linux 2_4_2 /proc/stat info
l2_4_2_stat = {
    'cpu'       : ['user', 'nice', 'system', 'idle'],
    'cpu0'      : ['user', 'nice', 'system', 'idle'],
    'cpu1'      : ['user', 'nice', 'system', 'idle'],
    'cpu2'      : ['user', 'nice', 'system', 'idle'],
    'cpu3'      : ['user', 'nice', 'system', 'idle'],
    'cpu4'      : ['user', 'nice', 'system', 'idle'],
    'cpu5'      : ['user', 'nice', 'system', 'idle'],
    'cpu6'      : ['user', 'nice', 'system', 'idle'],
    'cpu7'      : ['user', 'nice', 'system', 'idle'],
    'cpu8'      : ['user', 'nice', 'system', 'idle'],
    'cpu9'      : ['user', 'nice', 'system', 'idle'],
    'cpu10'     : ['user', 'nice', 'system', 'idle'],
    'cpu11'     : ['user', 'nice', 'system', 'idle'],
    'page'      : ['in', 'out'],
    'swap'      : ['in', 'out'],
    'intr'      : ['interrupts'],
    'disk_io'   : ['unknown1', 'unknown2', 'unknown3'],
    'ctxt'      : ['context_switches'],
    'btime'     : ['boot_time'],
    'processes' : ['processes'],
    }

version_map = {
    ('2','2','18'): { 'procstat' : l2_2_18_procstat,
                      'loadavg' : l2_2_18_loadavg,
                      'uptime' : l2_2_18_uptime,
                      'stat': l2_2_18_stat,
                      'procstatm' : l2_2_18_procstatm,
                      },
    ('2','4','2') : { 'procstat' : l2_2_18_procstat,
                      'loadavg' : l2_2_18_loadavg,
                      'uptime' : l2_2_18_uptime,
                      'stat': l2_4_2_stat,
                      'procstatm' : l2_2_18_procstatm,
                      },
    }

version_guess_map = {
    ('2', '2')  :  ('2', '2', '18'),
    ('2', '4')  :  ('2', '4', '2'),
    }

def get_struct(v, vmap=version_map.get, guess=version_guess_map.get):
    return vmap(v) or vmap(guess(tuple(v[:2])))

def get_kernel_version():
    version_match = re.compile(r'(\d+)\.(\d+)\.(\d+)').search
    s = open('/proc/version').readline()
    match = version_match(s)
    return (match.group(1), match.group(2), match.group(3))

VERSION = get_kernel_version()

def proc_statm(pid):
    return get_dict('procstatm', '/proc/%s/statm' % pid)
    
def self_statm():
    return get_dict('procstatm', '/proc/self/statm')

def proc_stat(pid):
    return get_dict('procstat', '/proc/%s/stat' % pid)

def self_stat():
    return get_dict('procstat', '/proc/self/stat')

def loadavg():
    return get_dict('loadavg', '/proc/loadavg')

def uptime():
    return get_dict('uptime', '/proc/uptime')

def stat():
    return get_multidict('stat', '/proc/stat')

def meminfo():
    """ very expensive on 2.2 kernels, not so on 2.4 kernels """
    lines = []; dict = {}
    for line in open('/proc/meminfo').readlines():
        if line:
            l = string.split(line)
            name, value = l[0], l[1:]
            if name in('total:', 'Mem:', 'Swap:'):
                continue
            key = string.lower(name)[:-1]
            value = value[0]
            if value and DIGITS.has_key(value[0]):
                value = maybe_number(value)
            dict[key] = value
    return dict

def getrunners(getsleepers=0, isdigit=DIGITS.has_key):
    running = []; swapped = []; blocked = []; sleeping = []
    addtorun   = running.append
    addtoswap  = swapped.append
    addtoblock = blocked.append
    addtosleep = sleeping.append
    names = os.listdir('/proc')
    for name in names:
        excp_happened = 0
        if isdigit(name[0]):
            try: stat = proc_stat(name)
            except: excp_happened = 1
            if excp_happened: continue
            state = stat['state']
            rss   = stat['rss']
            if getsleepers and state == "S":
                addtosleep(name)
            elif state == "R":
                if rss > 0: addtorun(name)
                else: addtoswap(name)
            elif state == "D":
                if rss > 0: addtoblock(name)
                else: addtoswap(name)
    if getsleepers:
        return running, blocked, swapped, sleeping
    else:
        return running, blocked, swapped

def get_dict(structname, filename, isdigit=DIGITS.has_key,
             find=string.find):
    lookup = get_struct(VERSION)[structname]
    d = {}; i = 0
    raw = string.split(open(filename).readline())
    for value in raw:
        if value and isdigit(value[0]):
            value = maybe_number(value)
        name = lookup[i]
        d[name] = value
        i = i + 1
    return d

def get_multidict(structname, filename, isdigit=DIGITS.has_key,
                  find=string.find):
    dict = {}
    lookup = get_struct(VERSION)[structname]
    for line in open(filename, 'r').readlines():
        l = string.split(line)
        category = l[0]
        if not lookup.has_key(category):
            continue
        items = l[1:]
        d = {}; i = 0
        for name in lookup[category]:
            value = items[i]
            if value and isdigit(value[0]):
                value = maybe_number(value)
            d[name] = value
            i = i + 1
        dict[category] = d
    return dict

def maybe_number(value, find=string.find, float=float, int=int):
    try:
        if find(value, '.') != -1:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value

if __name__ == '__main__':
    import time
    start = time.time()
    for x in xrange(100):
        print x
        getrunners()
        uptime()
        loadavg()
        self_statm()
        self_stat()
        stat()
        meminfo()
    end = time.time()
    print end-start
    #import sys
    #sys.exit(0)
    for key, value in self_stat().items():
         print key, value
    for key, value in loadavg().items():
          print key, value
    for key, value in uptime().items():
          print key, value
    for key, value in stat().items():
          print key, value
    for key, value in meminfo().items():
          print key, value
    for key, value in self_statm().items():
          print key, value


