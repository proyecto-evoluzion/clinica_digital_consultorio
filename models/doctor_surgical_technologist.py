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

class SurgicalTechnologist(models.Model):
	_name = "doctor.surgical.technologist"

	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
	room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment')
	recount_ids = fields.One2many('doctor.surgical.technologist.recount', 'surgical_technologist_id', string='Recount')


class SurgicalTechnologistRecount(models.Model):
	_name = "doctor.surgical.technologist.recount"

	surgical_technologist_id = fields.Many2one('doctor.surgical.technologist', string='Surgical technologist', ondelete='restrict')
	recount = fields.Many2one('doctor.surgical.technologist.element', string='Recount')
	start = fields.Integer(string='Starts')
	end = fields.Integer(string='End')

class SurgicalTechnologistElements(models.Model):
	_name = "doctor.surgical.technologist.element"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	active = fields.Boolean(string="Active", default=True)
