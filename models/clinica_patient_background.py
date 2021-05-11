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

from odoo import tools
import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError

class PlasticSurgerySheet(models.Model):
    _name = "clinica.patient.background"
    _rec_name = 'patient_id'
    
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    background_type = fields.Text(string='Background Type')
    background = fields.Text(string='Background')
    complete_format_id = fields.Many2one('complete.clinica.plastic.surgery', string='FCC')

class ConfigBackground(models.Model):
    _name = "config.clinica.patient.background"
    
    background_type = fields.Text(string='Background Type')
    background = fields.Text(string='Background')


class ClinicaPatientBackgroundType(models.Model):
	_name ="clinica.patient.background.type"

	name = fields.Char(string="Name backgroud")
	code = fields.Char(string="code background")
#############################################################################################

# Modelo para antecedentes generales

class BackgroundType(models.Model):
    _name ="background.type"
    _rec_name = 'type_background'


    type_background = fields.Char(string="Tipo")

class CopyBackgroundType(models.Model):
    _name ="copy.background.type"
    _rec_name = 'type_background'


    type_background = fields.Many2one('background.type',string="Tipo")
    value_background = fields.Text(string="Descripción")

class BackgroundCenter(models.Model):
    _name ="background.center"
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('doctor.patient',string="Paciente")
    background_ids = fields.Many2many('copy.background.type',string="Antecedentes")

# Modelo para antecedentes ginecologicos

class BackgroundGynecology(models.Model):
    _name ="background.gynecology"


    g = fields.Char(string="G")
    p = fields.Char(string="P")
    c = fields.Char(string="C")
    a = fields.Char(string="A")
    fur = fields.Date(string="FUR")
    fup = fields.Date(string="FUP")
    mpf = fields.Char(string="MPF")
    backgroud_gynecology_date = fields.Datetime(string="Fecha de Antecedentes")
    gynecology_id = fields.Many2one('complete.clinica.plastic.surgery', string="Ginecology")
    backgroun_patient_id = fields.Many2one('doctor.patient', string="Paciente")

    
# Modelo para antecedentes Paraclinicos

class BackgroundParaclinical(models.Model):
    _name ="background.paraclinical"


    attention_id = fields.Many2one('complete.clinica.plastic.surgery',string="Atencion Clinica")
    paraclinical = fields.Text(string="Paraclínicos")
    date = fields.Date(string="Fecha de registro")
    active = fields.Boolean(string="Active", default=True)
    patient_id = fields.Many2one('doctor.patient', string="Paciente")
   
  


