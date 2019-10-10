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


class ClinicaTextTemplate(models.Model):
    _name = "clinica.text.template"
    _order = 'id desc'
    _description = 'Clinica Template'
    
    name = fields.Char(string='Template Name')
    user_id = fields.Many2one('res.users', string="User")
    template_text = fields.Text(string='Template Text')
    type = fields.Selection([('quirurgic_description','Quirurgic Description'),
                             ('epicrisis','Epicrisis'),
                             ('medical_recipe','Medical Orders and Recipe')], string='Template Type')
    
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:




