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