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


from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = "res.partner"
    
    professional_created = fields.Boolean(string="Professional Created", copy=False)
    is_assurance = fields.Boolean(string="Is it an Assurance Company?", copy=False)
    patient_id = fields.Many2one('doctor.patient',string='Assurance C')
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')
    code_assurance = fields.Char(string="Code Assurance")
    type_user = fields.Selection([('1','1-Contributivo'),('2','2-Subsidiado'),('3','3-Vinculado'),
    	                        ('4','4-Particular'),('5','5-Otro'),('6','6-Víctima con afiliación al Régimen Contributivo'),
    	                        ('7','7-Víctima con afiliación al Régimen subsidiado'),('8','8-Víctima no asegurado (Vinculado)')]
    	                        ,string="Type User")
    tdoc_rips = fields.Selection([('CC','CC - Cedula de ciudadania'),('CE','CE - Cedula de extranjeria'),
                                      ('PA','PA - Pasaporte'),('RC','RC - Registro civil'),('TI','TI - Tarjeta de identidad'),
                                      ('AS','AS - Adulto sin identificar'),('MS','MS - Menor sin identificar'),
                                      ('CD','CD - Carnet diplomatico'),('SC','SC - Salvaconducto'),
                                      ('PE','PE - Permiso de permanencia'),
                                      ('CN','CN - Certificado de nacido vivo')], string='Type of Document')
    number_identification = fields.Char(string="Number Identification")
   

    
    
        
        
        