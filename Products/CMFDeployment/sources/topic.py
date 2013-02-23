"""
Topic Sources are zmi topics, aka canned catalog queries.

$Id: topic.py 1205 2006-03-04 23:04:46Z hazmat $
"""

# import check that zmi topics are present 
from Products.ZMITopic.topic import ZMITopic

from Globals import DTMLFile
from OFS.Folder import Folder
from Products.CMFDeployment.DeploymentInterfaces import IContentSource
from base import BaseSource

def addTopicSource( self,
                    id,
                    title='',
                    RESPONSE=None):

    """
    add a topic source
    """

    self._setObject( id, TopicSource( id, title ) )

    if RESPONSE:
        RESPONSE.redirect('manage_workspace')

addTopicSourceForm = DTMLFile('../ui/SourceTopicForm', globals())

class TopicSource( ZMITopic, BaseSource ):

    meta_type = "Topic Content Source"

    xml_factory = 'addTopicSource'

    icon_path = "topic_icon.gif"
    icon = BaseSource.icon
    
    __implements__ = IContentSource

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    def getContent(self):
        for res in self.queryCatalog():
            yield res
