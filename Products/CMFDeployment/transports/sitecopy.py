##################################################################
#
# (C) Copyright 2004-2005 Kapil Thangavelu and Contributors
#
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
Transfer deployed content via ftp or webdav using sitecopy.
$Id: sitecopy.py 1657 2006-09-13 22:00:32Z hazmat $
"""

from Products.CMFDeployment.DeploymentInterfaces import IDeploymentProtocol, IDeploymentTarget
from Products.CMFDeployment.lib import pexpect
from Products.CMFDeployment.DeploymentExceptions import ProtocolError
from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.utils import SerializablePlugin
from os import path
from cStringIO import StringIO

""" sitecopy config options

       site sitename
          server server-name
          remote remote-root-directory
          local local-root-directory
        [ port port-number ]
        [ username username ]
        [ password password ]
        [ proxy-server proxy-name
          proxy-port port-number ]
        [ url siteURL ]
        [ protocol { ftp | webdav } ]
        [ ftp nopasv ]
        [ ftp showquit ]
        [ ftp { usecwd | nousecwd } ]
        [ http expect ]
        [ http secure ]
        [ safe ]
        [ state { checksum | timesize } ]
        [ permissions { ignore | exec | all | dir } ]
        [ symlinks { ignore | follow | maintain } ]
        [ nodelete ]
        [ nooverwrite ]
        [ checkmoved [renames] ]
        [ tempupload ]
        [ exclude pattern ]...
        [ ignore pattern ]...
        [ ascii pattern ]...
"""        

class SiteCopyProtocol(object):

    __implements__ = IDeploymentProtocol

    def execute(self, target, structure):

        # you need to setup .sitecopyrc
        host = target.getHost()

        rcfile = CLIENT_HOME + '/.sitecopyrc'
        storepath = CLIENT_HOME + '/.sitecopy'
        command = 'sitecopy --rcfile=%s --storepath=%s' % (
            target._rcfile, target._storepath)

        rendered_command = '%s %s %s' % (command, '-uk', host)

        log = StringIO()
        conn = pexpect.spawn(rendered_command)
        conn.setlog(log)
        conn.expect(pexpect.EOF, 30) # 30 s timeout
        
        if conn.isalive():
            conn.kill(1)

        if conn.exitstatus != 0:
            log.seek(0)
            raise ProtocolError, log.read()

addSiteCopyTransportForm = DTMLFile('../ui/SiteCopyTransportAddForm', globals())

def addSiteCopyTransport( self,
                          id,
                          rcfile='',
                          storepath='',
                          RESPONSE=None):
    """ add site copy transport """
    
    transport = SiteCopyTransport( id )
    transport.edit( rcfile, storepath )
    self._setObject( id, transport )
    
    if RESPONSE is not None:
        RESPONSE.redirect('manage_main')

class SiteCopyTransport( SerializablePlugin ):

    __implements__ = IDeploymentTarget

    meta_type = 'SiteCopy Target'
    
    security = ClassSecurityInfo()

    _tprotocol = SiteCopyProtocol()
    xml_factory = "addSiteCopyTransport"
    
    manage_options = (
        
        {'label':'Settings',
         'action':'target_settings'},

        ) + App.Undo.UndoSupport.manage_options

    target_settings = DTMLFile('../ui/SiteCopyTransportSettingsForm', globals())

    def __init__(self, id):
        self.id = id
        self._rcfile = None
        self._storepath = None
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self,
             rcfile,
             storepath,
             RESPONSE=None):
        """ edit transport """

        self.checkRCFile( rcfile )
        self.checkStorePath( storepath )

        self._rcfile = path.abspath(path.expandvars(path.expanduser( rcfile )))
        self._storepath = storepath

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def checkRCFile( self, rcfile ):
        if not path.exists(
                  path.abspath(
                     path.expandvars(
                        path.expanduser( rcfile )
                        )
                     )
                  ):
            raise SyntaxError("invalid rcfile %s"%rcfile)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getRCFile')
    def getRCFile(self):
        return self._rcfile

    def checkStorePath( self, storepath ):
        pass

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getStorePath')
    def getStorePath(self):
        return self._storepath
    
    security.declareProtected(CMFCorePermissions.ManagePortal, 'transfer')
    def transfer(self, structure ):
        protocol = self.getProtocol()
        protocol.execute( self, structure)
        
    security.declareProtected(CMFCorePermissions.ManagePortal, 'getProtocol')
    def getProtocol(self):
        return self._tprotocol

    security.declarePrivate('getInfoForXml')
    def getInfoForXml( self ):
        d = SerializablePlugin.getInfoForXml( self )
        del d['attributes']['title']
        d.update( {
            'rcfile':self._rcfile,
            'storepath':self._storepath
                  } )
        return d
        
        
InitializeClass( SiteCopyTransport )
