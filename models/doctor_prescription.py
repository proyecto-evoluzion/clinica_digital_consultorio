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
import html2text

class DoctorPrescription(models.Model):
	_name = "doctor.prescription"

	@api.model
	def _get_signature(self):
		user = self.env.user
		signature = html2text.html2text(user.signature)
		return signature

	name= fields.Char(string="Order Type", required="1")
	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	prescription_date = fields.Date(string='Date', default=fields.Date.context_today)
	doctor_id = fields.Many2one('doctor.professional', string='Professional')
	profession_type = fields.Selection([('plastic_surgeon','Plastic Surgeon'),('anesthesiologist','Anesthesiologist'),
										('technologists','Surgical Technologists'),('helpers','Surgical Helpers'),
										('nurse','Nurse')], 
										string='Profession Type', default='plastic_surgeon', related="doctor_id.profession_type")
	order = fields.Text(string="Order", required="1")
	template_id = fields.Many2one('doctor.prescription.template', string='Template')
	sign_stamp = fields.Text(string='Sign and médical stamp', default=_get_signature)
	numberid = fields.Char(string='Number ID', related='patient_id.name')	

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			self.order = self.template_id.description

	@api.onchange('patient_id')
	def onchange_number(self):
		if self.patient_id:
			self.numberid = self.patient_id.ref

	@api.model
	def create(self, vals):
		ctx = self._context
		if ctx.get('uid'):
			create_uid = self.env['res.users'].search([('id','=',ctx.get('uid'))])
			professional_obj = self.env['doctor.professional'].search([('res_user_id','=',create_uid.id)])
			if professional_obj:
				vals['doctor_id'] = professional_obj.id

		res = super(DoctorPrescription, self).create(vals)
		return res 			

	@api.multi
	def _set_visualizer_default_values(self):
		vals = {
			'default_patient_id': self.patient_id and self.patient_id.id or False,
			'default_view_model': 'prescription',
			}
		return vals

	@api.multi
	def action_view_clinica_record_history(self):
		context = self._set_visualizer_default_values()
		return {
                'name': _('Clinica Record History'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'clinica.record.list.visualizer',
                'view_id': self.env.ref('clinica_digital_consultorio.clinica_record_list_visualizer_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }           

class DoctorPrescription(models.Model):
	_name = "doctor.prescription.template"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	description = fields.Text(string="Description", required="1")
	active = fields.Boolean(string="Active", default=True)
