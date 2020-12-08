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
import datetime

class DoctorPrescription(models.Model):
  _name = "doctor.prescription"
  _rec_name = 'patient_id'

  @api.model
  def _get_signature(self):
    user = self.env.user
    signature = html2text.html2text(user.signature)
    return signature

  def _get_professional(self):
    user = self.env.user
    professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user.id)])
    return professional_obj

  def _default_company(self):
    return self.env.ref('base.main_company').id

  @api.depends('inability_start_date', 'inability_end_date')
  def _compute_days(self):
  	for rec in self:
  		if rec.inability_start_date and rec.inability_end_date:
  			start = datetime.datetime.strptime(rec.inability_start_date, "%Y-%m-%d")
  			end = datetime.datetime.strptime(rec.inability_end_date, "%Y-%m-%d")
  			minus = start - end
  			minus = str(minus)
  			if len(minus) == 16:
  				rec.inability_total_days = minus[1:2]
  			elif len(minus) == 17:
  				rec.inability_total_days = minus[1:3]
  			else:
  				rec.inability_total_days = minus[1:4]

  name= fields.Char(string="Nombre del informe")
  order_type= fields.Selection([('informs','Informes y otros'),
                ('medicines','Medicamentos'),
                ('exam','Laboratorios'),
                ('inability','Incapacidad')],
                string="Tipo de orden", required="1", default='informs')
  prescription_date = fields.Date(string='Fecha', default=fields.Date.context_today)
  inability_start_date = fields.Date(string='Fecha Inicio', default=fields.Date.context_today)
  inability_end_date = fields.Date(string='Fecha Finalización')
  inability_total_days = fields.Char(string='Duración (en días)', compute=_compute_days)
  patient_id = fields.Many2one('doctor.patient', 'Paciente', ondelete='restrict', required="0")
  complete_format_id = fields.Many2one('complete.clinica.plastic.surgery', 'Atencion', ondelete='restrict')
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
  atc_ids = fields.One2many('doctor.atc_medicine','prescription_id', string="ATC")
  load_register = fields.Boolean(string='-', default=False)
  company_id = fields.Many2one('res.company',string='Company', default=_default_company)

  

  @api.onchange('template_id')
  def onchange_template_id(self):
    if self.template_id:
      self.order = self.template_id.description

  @api.onchange('name')
  def onchange_name(self):
    if self.name:
      self.name = str(self.name).upper()

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

	cups_id = fields.Many2one('doctor.cups.code', 'CUPS', ondelete='restrict', domain=[('procedure_type','in',['3','4','5'])])
	prescription_id = fields.Many2one('doctor.prescription', 'Prescription Exam')
	qty = fields.Integer(string="Cantidad")
	indications = fields.Char(string="Indicaciones")
