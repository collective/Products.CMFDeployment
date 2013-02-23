#!/usr/bin/env python2.1
"""

Python script meant to be called via cron which uses httplib to call
the garbage collection method on a session data manager (for use when
synchronous garbage collection is not employed.

"""

import sys, httplib, string, base64, getopt, traceback, time

def method_caller(server, method, user, password):
    h = httplib.HTTP(server)
    h.putrequest('GET', method)
    h.putheader('User-Agent', 'Zope method caller')
    h.putheader('Accept', 'text/html')
    h.putheader('Accept', 'text/plain')
    h.putheader('Host', server)
    if user and password:
        h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
            base64.encodestring("%s:%s" % (user, password)),
            "\012", ""))
    h.endheaders()
    errcode, errmsg, headers = h.getreply()
    if errcode != 200:
        f = h.getfile()
        data = f.read()
        f.close()
        print data

if __name__ == '__main__':
    usage = ("Usage:\n%s -s servername:port -m methodname -u username "
             "-p password -c continuous(secs)\n%s -h (prints this help)\n\n"
             % (sys.argv[0], sys.argv[0]))
    opts, args = getopt.getopt(sys.argv[1:], 's:m:u:p:c:h')
    server = None
    method = None
    user = None
    password = None
    period = None
    for o, a in opts:
        if o == '-s':
            server = a
        if o == '-m':
            method = a
            if method[0] != '/':
                method = '/' + method
            if method[-1] == '/':
                method = method[:-1]
        if o == '-u':
            user = a
        if o == '-p':
            password = a
        if o == '-h':
            print usage
            sys.exit()
        if o == '-c':
            period = int(a.strip())
    if not server:
        print usage + 'Error: need a server name via -s'
        sys.exit(1)
    elif not method:
        print usage + 'Error: need a method name via -m, e.g. /getnews'
        sys.exit(1)
    elif not user:
        print usage + 'Error: need a user name via -u'
        sys.exit(1)
    elif not password:
        print usage + 'Error: need a password via -p'
        sys.exit(1)

    while 1:
        try:
            method_caller(server, method, user, password)
        except:
            traceback.print_exc()
        if period is None: break
        time.sleep(period)

            
