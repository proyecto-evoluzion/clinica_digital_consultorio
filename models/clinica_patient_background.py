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
    
    
    # consultation_reason = fields.Text(string="Reason for Consultation", related="patient_id.consultation_reason")
    # pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    # surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    # toxic = fields.Text(string="Toxic")
    # allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    # gyneco_obst = fields.Text(string="Gyneco-Obstetricians")
    # relatives = fields.Text(string="Relatives")
    # others = fields.Text(string="Others")
    # paraclinical = fields.Text(string="Paraclinical")

    # smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    # cigarate_daily = fields.Integer(string="Cigarettes / Day", related='patient_id.cigarate_daily')
    # smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
    #                               ('year','per Year')], string="Smoke Unit of Measure", default='day', related='patient_id.smoke_uom')
    # is_alcoholic = fields.Boolean(string="Alcoholic Drinks", related='patient_id.is_alcoholic')
    # alcohol_frequency = fields.Integer(string="Frequency", related='patient_id.alcohol_frequency')
    # alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
    #                                           ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day', 
    #                                          related='patient_id.alcohol_frequency_uom')
    # marijuana = fields.Boolean(string="Marijuana", related='patient_id.marijuana')
    # cocaine = fields.Boolean(string="Cocaine", related='patient_id.cocaine')
    # ecstasy = fields.Boolean(string="Ecstasy", related='patient_id.ecstasy')
    # body_background_others = fields.Text(string="Body Background Others", related='patient_id.body_background_others')
    # pharmacological = fields.Text(string="Pharmacological", related='patient_id.pharmacological')
    # pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    # child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    
    # gestations = fields.Integer(string="G", help="Gestations")
    # births = fields.Integer(string="B",  help="Births")
    # cesarean = fields.Integer(string="C", help="Cesarean")
    # abortion_number = fields.Integer(string="A", related='patient_id.abortion_number', help="Abortions")
    # last_menstruation_date = fields.Date(string="LMD", related='patient_id.last_menstruation_date', help="Last menstruation date")
    # last_birth_date = fields.Date(string="LBD", related='patient_id.last_birth_date', help="Last birth date")
    # mature_promoting_factor = fields.Char(string="MPF",  help="Mature Promoting Factor")

    # contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    # diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    # hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    # arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    # thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
