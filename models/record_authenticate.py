# -*- coding: utf-8 -*-
###############################################################################
#
#    BroadTech IT Solutions Pvt Ltd
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

class RecordAuthenticate(models.Model):
    _name = "record.authenticate"
    _description = 'To validate the user before gets saving a record'
    
    name = fields.Char('Identifier')
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    
    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.name = self.model_id.name or ''
    
    @api.model
    def autenticate_user(self, url, db, username, password, model):
        is_model_exists = self.env['record.authenticate'].search([('model_id', 'in', model or [])])
        if is_model_exists :
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url), allow_none=True)
            uid = common.authenticate(db, username, password, {})
            if(uid):
                return 1
            else:
                return 0 
        else:
            return 1
        
    @api.model
    def check_model(self, model):
        is_model_exists = self.env['record.authenticate'].search([('model_id', 'in', model or [])])
        if is_model_exists :
            return 1 
        else:
            return 0
        