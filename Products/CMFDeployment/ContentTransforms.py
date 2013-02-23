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
Purpose: Transforms for Rendered Content Before Storage
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
License: GPL
Created: 8/10/2002
$Id: ContentTransforms.py 1398 2006-06-27 19:02:51Z hazmat $
"""

from Namespace import *
from Log import LogFactory
from Products.CMFCore.Expression import Expression
from ExpressionContainer import ExpressionContainer, getDeployExprContext
from transforms.registry import getTransform, listTransforms

log = LogFactory('Storage Transform')

class ContentTransforms(Folder):

    meta_type = 'Content Transforms'

    security = ClassSecurityInfo()

    manage_options = (

        {'label':'Overview',
         'action':'overview'},
        
        {'label':'Transforms',
         'action':'rules/manage_main'},

        {'label':'Policy',
         'action':'../overview'}

        )

    overview = DTMLFile('ui/ContentTransformsOverview', globals())

    xml_key = 'content_transforms'
    
    def __init__(self, id):
        self.id = id
        self.enabled = 0

    security.declarePrivate('transform')
    def transform(self, descriptor, rendered, file_path):
        
        if not self.enabled:
            return rendered

        portal  = getToolByName(self,'portal_url').getPortalObject()
        content = descriptor.getContent()
        context = getDeployExprContext(content, portal)
        for fr in self.rules.objectValues('Content Transform Rule'):
            if not fr.valid(context):
                continue
            
            try:
                script = getTransform(fr.script_id)
            except:
                log.warning('Content Transform Script %s Not Found'%str(fr.script_id))
                continue
            try:
                rendered = script(descriptor, rendered, file_path)
            except:
                log.warning('Content Transform Exception from %s on %s '%(
                    fr.script_id,
                    descriptor.content_url)
                )
                
        return rendered

    def editTransforms(self, enable_flag, RESPONSE=None):
        """ """
        self.enabled = not not int(enable_flag)
        if RESPONSE:
            RESPONSE.redirect('./overview')
        
    def manage_afterAdd(self, item, container):
        if self._getOb('rules', None) is None:
            ob = TransformRulesContainer('rules')
            self._setObject('rules', ob)

    def getInfoForXml( self ):
        res = []
        for transform in self.rules.objectValues():
            res.append( transform.getInfoForXml() )

        if not res:
            return {}
        return {'attributes':{ 'enabled':bool( self.enabled ) },
                'transforms': res }
            

class ContentTransformRule(SimpleItem):

    meta_type = 'Content Transform Rule'

    manage_options = (
        {'label':'Rule',
         'action':'editRuleForm'},
        {'label':'All Rules',
         'action':'../manage_main'},
        {'label':'Content Transforms',
         'action':'../../overview'}
        )
    
    editRuleForm = DTMLFile('ui/ContentTransformEditForm', globals())
    
    def __init__(self, id, condition, script_id):
        self.id = id
        self.condition = Expression(condition)
        self.condition_text = condition
        self.script_id = script_id
        
    def valid(self, context):
        return not not self.condition(context)

    def editRule(self, condition, script_id, RESPONSE=None):
        """ """

        assert script_id in listTransforms(), "Invalid Transform Id"
        
        self.condition = Expression(condition)
        self.condition_text = condition
        self.script_id = script_id

        if RESPONSE is not None:
            RESPONSE.redirect('../manage_main')

    def getInfoForXml( self ):
        return dict(
            product='container',
            factory='addRule',
            id = self.id,
            condition = self.condition_text,
            script_id = self.script_id )
    
        
class TransformRulesContainer(ExpressionContainer):

    meta_type = 'Content Transform Rules Container'

    manage_options = (
        {'label':'Rules',
         'action':'manage_main'},

        {'label':'Content Transforms',
         'action':'../overview'},        

        {'label':'Policy',
         'action':'../../overview'}
        )

    addRuleForm = DTMLFile('ui/ContentTransformAddForm', globals())

    all_meta_types = (
        {'name':ContentTransformRule.meta_type,
         'action':'addRuleForm'},
        )

    def __init__(self, id):
        self.id = id

    def listTransformScripts(self):
        return listTransforms()

    def addRule(self, id, condition, script_id, RESPONSE=None):
        """ """

        assert script_id in listTransforms(), "Invalid Transform Id"
        
        rule = ContentTransformRule(id=id,
                                 condition=condition,
                                 script_id=script_id)
        
        self._setObject(id, rule)

        if RESPONSE is not None:
            RESPONSE.redirect('manage_main')
    

