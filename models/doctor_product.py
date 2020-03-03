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


import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

class HealthProcedures(models.Model):
    _inherit = "product.product"
    
    is_health_procedure = fields.Boolean('Is Health Procedure?')
    procedure_code = fields.Char('Code', size=16)
    procedure_type = fields.Selection([('1', 'Consultation'), ('2', 'Surgical Procedure'),
                                        ('3', 'Diagnostic Image'), ('4', 'Clinical laboratory'),
                                        ('5', 'Therapeutic Procedure'), ('6', 'Hospitalization'),
                                        ('7', 'Odontological'), ('8', 'Other')], 'Procedure Type')
    

class DoctorCupsCode(models.Model):
    _name = "doctor.cups.code"
    _rec_name = 'product_id'
    
    code = fields.Char(related='product_id.procedure_code', string='Code', size=16, store=True)
    product_id = fields.Many2one('product.product', string='Health Procedure', ondelete='restrict')
    
    
    
    
    
    