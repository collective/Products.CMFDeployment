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
Purpose: general utility functions
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2006
License: GPL
Created: 8/10/2002
$Id: utils.py 1957 2007-05-14 07:26:27Z hazmat $
"""


import inspect, sys
from Acquisition import aq_base, Implicit
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
import OFS, App


class ContentModificationInspector( Implicit ):

    def __call__(self):
        return DateTime()
    
## while more conceptually beholden, the below isn't correct for
## subobject modification, the above insteads binds to index time
#
#        content = self.aq_parent
#        if content._p_changed:
#            return DateTime()
#        return content.bobobase_modification_time()

class SerializablePlugin( SimpleItem ):

    meta_type = 'Serializable Plugin'
    xml_template = None
    xml_factory  = None

    def toXml(self):
        # compatiblity method
        assert self.xml_template, self.xml_factory
        data = self.getInfoForXmlTemplate()
        if data is None:
            return ''
        return self.xml_template%( data )

    def getInfoForXmlTemplate(self):
        # compatiblity method
        info = self.getInfoForXml()
        info.update( info['attributes'] )
        del info['attributes']
        return info
        
    def getInfoForXml(self):
        """
        get a dictionary of info for xml formatting
        """
        # stateful sources should override
        
        module = inspect.getmodule( self.__class__ )
        parts = module.__name__.split('.')
        
        if 'Products' not in parts:
            return

        idx = parts.index('Products')
        product = ".".join(parts[idx+1:idx+2])
        
        d = { 'attributes': { 'id': self.id,
                              'title': self.title_or_id(),
                              'product': product,
                              'factory': self.xml_factory } }

##         d = { 'id': self.id,
##               'title': self.title_or_id(),
##               'product': product,
##               'factory': self.xml_factory } 

        return d


def getXmlPath( self ):
    res = []
    policy = self.getPolicy()
    
    idx = self.aq_chain.index( policy )

    chain = self.aq_chain[idx:]
    for c in chain:
        res.append( c.xml_key )

    filter( None, res )
    return ".".join( res )
    

class BoundFunction( object ):

    def __init__(self, func, args, kw):
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self):
        return self.func( *self.args, **self.kw )

    def __str__( self ):
        return "Bound Func", self.func
    
def bind( func, *args, **kw ):
    # really a curried func
    return BoundFunction( func, args, kw )
    

def guess_filename( content ):
    cid = content.getId()
    if '.' in cid and ( len(cid)-cid.rfind('.') ) < 5 : 
        #print 'gf id', cid
        return content.id
    elif '.' in content.title:
        #print 'gf ti', content.title
        return content.title
    elif hasattr(content, 'content_type') and content.content_type:
        if callable(content.content_type):
            content_type = content.content_type()
        else:
            content_type = content.content_type
        major, minor = content_type.split('/')
        if major == 'text' and minor == 'plain':
            minor = 'html'
        if major == 'text' and minor == 'structured':
            minor = 'html'
        if major == 'text' and minor == 'x-rst':
            minor = 'html'
        #print 'gf m', "%s.%s"%(cid,minor)
        return "%s.%s"%(cid, minor)
    
    raise RuntimeError("Could not Determine Extension ")
    

def registerIcon(filename):
    """
    verbatim from mailing list post
    http://zope.nipltd.com/public/lists/zope-archive.nsf/ByKey/EF7C85E6A2AA8FDA
    """    
    # A helper function that takes an image filename (assumed
    # to live in a 'www' subdirectory of this package). It 
    # creates an ImageFile instance and adds it as an attribute
    # of misc_.MyPackage of the zope application object (note
    # that misc_.MyPackage has already been created by the product
    # initialization machinery by the time registerIcon is called).

    setattr(OFS.misc_.misc_.CMFDeployment, 
            filename, 
            App.ImageFile.ImageFile('www/%s' % filename, globals())
            )

def safe_traverse( object, path ):
    try:
        return object.restrictedTraverse( path )
    except AttributeError:
        return None

def file2string(o):
    """ transform a zope file object into a string """
    
    (start,end) = (0,o.get_size())
    data = o.data
    if type(data) is type(''): #StringType
        return data[start:end]
    else: # blob chain
        pos = 0
        buf = [] #infile = StringIO(data.data)
        w = buf.append
        while data is not None:
            l =  len(data.data)
            pos = pos + l
            if pos > start:
                # We are within the range
                lstart = l - (pos - start)

                if lstart < 0: lstart = 0
                
                # find the endpoint
                if end <= pos:
                    lend = l - (pos - end)
                    w(data[lstart:lend])
                    break

                w(data[lstart:])

            data = data.next

    return ''.join(buf)


try:
    from Products.Archetypes.BaseUnit import BaseUnit
    AT_FOUND = True
except ImportError:
    AT_FOUND = False
    
def is_baseunit( ob ):
    if not AT_FOUND:
        return False
    return isinstance( aq_base(ob), BaseUnit )


# junk to work around bad apis in atct
try:

    from Products.ATContentTypes.lib import calendarsupport
    from StringIO import StringIO
    
    def event_ics_view( content ):
        out = StringIO()
        out.write( calendarsupport.ICS_HEADER % { 'prodid' : calendarsupport.PRODID } )
        out.write( content.getICal() )
        out.write( calendarsupport.ICS_FOOTER)
        return out.getvalue()

    def event_vcs_view( content ):
        out = StringIO()
        out.write( calendarsupport.VCS_HEADER % { 'prodid' : calendarsupport.PRODID, })
        out.write( content.getVCal())
        out.write( calendarsupport.VCS_FOOTER)
        return out.getvalue()

except:
    event_ics_view = None
    event_vcs_view = None

# occasionally 
def traverse_safe( content, path ):
    try:
        return content.restrictedTraverse( path )
    except AttributeError:
        return None

# taken from code i wrote for proxyindex

# used latter when constructing an object wrapper to determine if the
# object is already wrapped.
try:
    from Products.CMFCore.CatalogTool import IndexableObjectWrapper, ICatalogTool
    CMF_FOUND = True
except ImportError:
    CMF_FOUND = False
    class ICatalogTool(Interface): pass
    IndexableObjectWrapper = None

try:
    from Products.CMFPlone.CatalogTool import ExtensibleIndexableObjectWrapper
    PLONE_FOUND = True
except:
    PLONE_FOUND = False
    ExtensibleIndexableObjectWrapper = None

def unwrap_object( obj ):

    if CMF_FOUND and isinstance( obj, IndexableObjectWrapper ):
        return obj._IndexableObjectWrapper__ob

    elif PLONE_FOUND and isinstance( obj, ExtensibleIndexableObjectWrapper ):
        return obj._obj
        
    return obj


def filter_meta_types(meta_types):
    """ a little silly but we're getting duplicates"""
    filtered = []
    for t in meta_types:
        if t['action'].startswith('manage_addProduct/Products.CMFDeployment'):
            filtered.append(t)
    # filter dups
    return filtered
