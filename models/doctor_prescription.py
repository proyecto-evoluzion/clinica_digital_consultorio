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

	def _get_professional(self):
		user = self.env.user
		professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user.id)])
		return professional_obj		

	name= fields.Char(string="Nombre del informe", required="1")
	order_type= fields.Selection([('informs','Informes y otros'),('medicines','Medicamentos'),('exam','Laboratorios')],
							string="Tipo de orden", required="1", default='informs')
	prescription_date = fields.Date(string='Fecha', default=fields.Date.context_today)
	patient_id = fields.Many2one('doctor.patient', 'Paciente', ondelete='restrict')
	patientname = fields.Char(string='# Historia Clínica', related='patient_id.name')
	numberid = fields.Integer(string='# Historia Clínica', related='patient_id.ref')
	user_type = fields.Selection([('contributory','Contributory'),('subsidized','Subsidized'),('linked','Linked'),('particular','Particular'),('other','Other'),('victim_contributive','Victim - Contributive'),('victim_subsidized','Victim - Subsidized'),('victim_linked','Victim - Linked')],string='Tipo de Usuario', related='patient_id.user_type')
	phone = fields.Char(string='Teléfono', related='patient_id.phone')
	sex = fields.Selection([('male','Male'), ('female','Female')],string='Género', related='patient_id.sex')
	residence_address = fields.Text(string='Dirección', related='patient_id.residence_address')
	doctor_id = fields.Many2one('doctor.professional', string='Professional', default=_get_professional)
	profession_type = fields.Selection([('plastic_surgeon','Plastic Surgeon'),('anesthesiologist','Anesthesiologist'),
										('technologists','Surgical Technologists'),('helpers','Surgical Helpers'),
										('nurse','Nurse')], 
										string='Profession Type', related="doctor_id.profession_type")
	prescription = fields.Text(string="Informe")
	template_id = fields.Many2one('doctor.prescription.template', string='Plantilla')
	images = fields.Html(string='Imagenes')
	# sign_stamp = fields.Text(string='Sign and médical stamp', default=_get_signature)

	exam_ids = fields.One2many('doctor.prescription.exam','prescription_id', string="Examen")

	

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			self.order = self.template_id.description

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

class DoctorPrescriptionTemplate(models.Model):
	_name = "doctor.prescription.template"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	description = fields.Text(string="Description", required="1")
	active = fields.Boolean(string="Active", default=True)

class DoctorPrescriptionExam(models.Model):
	_name = "doctor.prescription.exam"
	_rec_name="cups_id"

	cups_id = fields.Many2one('doctor.cups.code', 'CUPS', ondelete='restrict')
	prescription_id = fields.Many2one('doctor.prescription', 'Prescription Exam')
	qty = fields.Integer(string="Cantidad")
	indications = fields.Char(string="Indicaciones")	
