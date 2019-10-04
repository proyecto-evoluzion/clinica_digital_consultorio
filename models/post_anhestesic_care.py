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


import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError

class ClinicaPostAnhestesicCare(models.Model):
	_name = "clinica.post.anhestesic.care"
	_order = 'id desc'
	_description = 'Post-Anhestesic care'

	patient_id = fields.Many2one('doctor.patient', 'Paciente', ondelete='restrict')
	medical_record= fields.Char(string='HC')
	bed = fields.Char(string='Cama')
	date = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	procedure = fields.Char(string='Procedimiento')
	duration = fields.Float(string='Duración (en horas)')
	surgeon_id = fields.Many2one('doctor.professional', string='Cirujano')
	anesthesiologist_id = fields.Many2one('doctor.professional', string='Anestesiólogo')
	nurse_id = fields.Many2one('doctor.professional', string='Auxiliar Enfermería')
	#vital signs
	vital_sign_ids = fields.One2many('post.anhestesic.care.vital.signs', 'post_anhestesic_care_id', string='Signos Vitales', copy=False)
	#liquids
	liquids_ids = fields.One2many('post.anhestesic.care.liquids', 'post_anhestesic_care_id', string='Líquidos', copy=False)
	drugs_ids = fields.One2many('post.anhestesic.care.drugs','post_anhestesic_care_id', string='Drogas', copy=False )
	observations_ids = fields.One2many('post.anhestesic.care.observations','post_anhestesic_care_id', string='Observaciones', copy=False )
	aldrete_ids= fields.One2many('post.anhestesic.care.aldrete','post_anhestesic_care_id', string='Escala Aldrete', copy=False )
	medical_orders_ids= fields.One2many('post.anhestesic.care.medical.orders','post_anhestesic_care_id', u'Órdenes Médicas')
	#selection anhestesia
	anhestesia = fields.Selection([('inhalatoria','Inhalatoria'),('intravenosa','Intravenosa'),('regional','Regional'),('peridural','Peridural'),('raquidea','Raquidea'),('bloqueo','Bloqueo'),('local','Local C.')], string='Anestésia')
	#selection airway
	airway = fields.Selection([('res_espontanea','Respiración Espontánea'),('canulao2','Cánula O2 L/min'),('venturi','Venturi%'),('iot_int','IOT INT'),('t_en_t','T en T'),('venti_mecanica','Ventilación mecánica'),('fr','FR'),('fi_o2','Fi O2'),('peep','PEEP'),('vc','V.C.')], string='Vía Aérea')
	#drains
	nasogastric_tube = fields.Integer(string='Tubo Nasogástrico')
	chest_tube = fields.Integer(string='Tubo Tórax')
	hemovac = fields.Integer(string='Hemovac')
	urinary_tube = fields.Integer(string='Sonda Vesical')
	cystostomy = fields.Integer(string='Sonda Cistostomía')
	others = fields.Integer(string='Otros')
	total = fields.Integer(string='Total (cc)', compute='_get_sum', store=True, help="Total in cubic centimeters")
	room_id = fields.Many2one('doctor.waiting.room', string="Surgery Room/Appointment", copy=False)
    
	@api.onchange('room_id')
	def onchange_room_id(self):
		if self.room_id:
			self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
	


	@api.depends('nasogastric_tube','chest_tube','hemovac','urinary_tube','cystostomy','others')
	def _get_sum(self):
		for rec in self:
			rec.total= rec.nasogastric_tube+rec.chest_tube+rec.hemovac+rec.urinary_tube+rec.cystostomy+rec.others
			


class PostAnhestesicCareVitalSigns(models.Model):
	_name = "post.anhestesic.care.vital.signs"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	vital_signs_date_hour = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	vital_signs_tas = fields.Integer(string='TAS')
	vital_signs_tad = fields.Integer(string='TAD')
	vital_signs_fc = fields.Integer(string='FC')
	vital_signs_fr = fields.Integer(string='FR')
	vital_signs_sao2 = fields.Integer(string='SaO2')
	vital_signs_pain  = fields.Integer(string='Dolor(0-10)')
	vital_signs_queasiness  = fields.Boolean(string="Náuseas")
	vital_signs_vomit  = fields.Boolean(string="Vómito")


class PostAnhestesicCareLiquids(models.Model):
	_name = "post.anhestesic.care.liquids"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#liquids
	liquid_via = fields.Char(string='Via')
	liquid_site = fields.Char(string='Sitio')
	liquid_type = fields.Char(string='Tipo')
	liquid_initial_amount = fields.Integer(string='Cant. Inicial (cc)')
	liquid_amount_recovery = fields.Integer(string='Cant. Recuperación (cc)')

class PostAnhestesicCareDrugs(models.Model):
	_name = "post.anhestesic.care.drugs"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#drugs
	drug_time = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	drug_name = fields.Char(string='Droga')
	drug_quantity = fields.Float(string='Cantidad')
	drug_via = fields.Char(string='Via')
	drug_dr = fields.Char(string='D.R.')
	
class PostAnhestesicObservations(models.Model):
	_name = "post.anhestesic.care.observations"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#observation
	observation_time = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	observation = fields.Char('Observaciones')

class PostAnhestesicAldrete(models.Model):
	_name = "post.anhestesic.care.aldrete"
	_score = 0
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#aldrete
	moment = fields.Selection([('1','Admisión'),('2','5'),('3','15'),('4','30'),('5','45'),('6','60'),('7','Alta')], string='Momento')
	conscience = fields.Selection([('2','Despierto'),('1','Responde Llamado'),('0','No Responde')], string='Conciencia')
	saturation = fields.Selection([('2','SO2 > 93% + Aire'),('1','SO2 > 90% + O2'),('0','SO > 90% + O2')], string='Saturación')
	breathing = fields.Selection([('2','Capaz de Toser'),('1','Disnea'),('0','Apnea')], string='Respiración')
	circulation = fields.Selection([('2','T/A ± 20%'),('1','T/A ± 20% - 50%'),('0','T/A ± 50%')], string='Circulación')
	activity = fields.Selection([('2','Mueve 4 Extremidades'),('1','Mueve 2 Extremidades'),('0','Inmóvil')], string='Actividad')
	aldrete_score = fields.Integer('Puntaje', compute='_compute_score')

	@api.multi
	@api.depends('conscience','saturation','breathing','circulation','activity')
	def _compute_score(self):
		if self.conscience:
			if self.conscience == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.conscience == '1':
				self.aldrete_score = int(self.aldrete_score)+ 1
			elif self.conscience == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

	
		if self.saturation:
			if self.saturation == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.saturation == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.saturation == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.breathing:
			if self.breathing == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.breathing == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.breathing == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.circulation:
			if self.circulation == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.circulation == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.circulation == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.activity:
			if self.activity == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.activity == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.activity == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

class PostAnhestesicMedicalOrders(models.Model):

	_name = 'post.anhestesic.care.medical.orders'
	_rec_name = 'procedures_id'


	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	plantilla_id = fields.Many2one('post.anhestesic.care.medical.orders.temp', 'Plantillas')
	prescripcion = fields.Char(u'Prescripción')
	procedures_id = fields.Many2one('product.product', 'Medicamento/Otro elemento', required=True)
	recomendacion = fields.Text('Recomendaciones')


