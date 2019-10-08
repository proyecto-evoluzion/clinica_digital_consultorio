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

class DoctorPrescription(models.Model):
	_name = "doctor.prescription"

	name= fields.Char(string="Order Type", required="1")
	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	prescription_date = fields.Date(string='Date', default=fields.Date.context_today)
	doctor_id = fields.Many2one('doctor.professional', string='Professional')
	profession_type = fields.Selection([('plastic_surgeon','Plastic Surgeon'),('anesthesiologist','Anesthesiologist'),
										('technologists','Surgical Technologists'),('helpers','Surgical Helpers'),
										('nurse','Nurse'),('otorhino','Otorhinolaryngologist')], 
										string='Profession Type', default='plastic_surgeon', related="doctor_id.profession_type")
	order = fields.Text(string="Order", required="1")
	template_id = fields.Many2one('doctor.prescription.template', string='Template')

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			self.order = self.template_id.description

class DoctorPrescription(models.Model):
	_name = "doctor.prescription.template"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	description = fields.Text(string="Description", required="1")
	active = fields.Boolean(string="Active", default=True)
