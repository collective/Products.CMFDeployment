from Products.CMFDeployment.DeploymentInterfaces import IDeploymentProtocol, IDeploymentTarget
from Products.CMFDeployment.lib import pexpect
from Products.CMFDeployment.DeploymentExceptions import ProtocolError
from Products.CMFDeployment.Namespace import *
from Products.CMFDeployment.utils import SerializablePlugin
from os import path, walk
from cStringIO import StringIO
from tarfile import open as opentar
from datetime import datetime
from zope.interface import implements

class ZipProtocol(object):
    """The ZipProtocol object actually does the work of compressing all the cooked pages to a compressed file.  
    Any work done on the compression level should happen here.
    """
    __implements__ = IDeploymentProtocol

    def execute(self, target, structure):
        """
        """
        local_directory = structure.getMountPoint()
        target_directory = target.getLocation()
        
        ds = datetime.now()
        zf = opentar(path.join(target_directory,"Export_%s-%s-%s_%s_%s_%s.tar.gz" % (ds.month, ds.day, ds.year, ds.hour, ds.minute, ds.second)), "w:gz")
        zf.posix = False         # set the file to allow names longer than 100 characters
        zf.add(local_directory, recursive=True)
        zf.close()
        

addZipTransportForm = DTMLFile('../ui/ZipTransportAddForm', globals())

def addZipTransport( self,
                          id,
                          location='',
                          RESPONSE=None):
    """ add zip transport """
    
    transport = ZipTransport( id )
    transport.edit( location )
    self._setObject( id, transport )
    
    if RESPONSE is not None:
        RESPONSE.redirect('manage_main')

class ZipTransport( SerializablePlugin ):
    """The Zip transport contains configuration information,
    security permissions, and providing information required
    for serializing the configuration to the CMFDeployment
    xml config export.
    """

    implements(IDeploymentTarget)

    meta_type = 'Zip Target'

    security = ClassSecurityInfo()

    _tprotocol = ZipProtocol()
    xml_factory = "addZipTransport"

    manage_options = (

        {'label':'Settings',
         'action':'target_settings'},

        ) + App.Undo.UndoSupport.manage_options

    target_settings = DTMLFile('../ui/ZipTransportSettingsForm', globals())

    def __init__(self, id):
        self.id = id
        self._location = None


    security.declareProtected(CMFCorePermissions.ManagePortal, 'edit')
    def edit(self,
             location,
             RESPONSE=None):
        """ edit transport """

        self.checkLocation( location )

        self._location = location

        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def checkLocation( self, location ):
        """Validation stub.
        """
        pass

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getLocation')
    def getLocation(self):
        """The only current relevant config option.  Directory 
        where compressed file is output.
        """
        return self._location

    security.declareProtected(CMFCorePermissions.ManagePortal, 'transfer')
    def transfer(self, structure ):
        """Triggers execution of compression.
        """
        protocol = self.getProtocol()
        protocol.execute( self, structure)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getProtocol')
    def getProtocol(self):
        return self._tprotocol

    security.declarePrivate('getInfoForXml')
    def getInfoForXml( self ):
        """Get serialization info for output config file.
        """
        d = SerializablePlugin.getInfoForXml( self )
        del d['attributes']['title']
        d.update( {
            'location':self._location
                  } )
        return d


InitializeClass( ZipTransport )