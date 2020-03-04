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

class DoctorAtc(models.Model):
    _name = "doctor.atc"
    _rec_name = "name"
    _description = 'ATC Record to prescribe'
    
    name = fields.Char('ATC')
    code = fields.Char('Code')


class DoctorAtcRoute(models.Model):
    _name = "doctor.atc_route"
    _rec_name = "name"    
    _description = 'ATC Record Indication'
    
    name = fields.Char('Route')


class DoctorAtc(models.Model):
    _name = "doctor.atc_use"
    _rec_name = "name"    
    _description = 'ATC Record use mode'
    
    name = fields.Char('Use mode')


class DoctorAtc(models.Model):
    _name = "doctor.atc_medicine"
    _rec_name = "atc_id"    
    _description = 'Medicine General Record'
    
    name = fields.Char(string='name',default="Medicinas")
    atc_id = fields.Many2one('doctor.atc', string='ATC')
    atc_route_id = fields.Many2one('doctor.atc_route', string='Route')
    atc_use_id = fields.Many2one('doctor.atc_use', string='Use mode')
    total_to_use = fields.Integer(string="To use")
    every_use = fields.Integer(string="Every use")
    deadline_use = fields.Integer(string="Deadline use")
    frequency_type1 = fields.Selection([('minute','Minutos'),('hour','Horas'),
										('day','Días'),('week','Semanas'),
										('month','Meses')],string='Frequency Type 1')
    frequency_type2 = fields.Selection([('minute','Minutos'),('hour','Horas'),('day','Días'),
										('week','Semanas'),('month','Meses'),
										('every','Indefinidamente')], 
										string='Frequency Type 2')
    indications = fields.Text(string="Indicaciones")
    prescription_id = fields.Many2one('doctor.prescription', 'Prescription ATC')    