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



class PatientAssurance(models.Model):
	_name = "patient.assurance"


	insurer_id = fields.Many2one('res.partner',string='Assurance Company', domain=[('is_assurance', '=', True)])
	type_user = fields.Selection([('1','1-Contributivo'),('2','2-Subsidiado'),('3','3-Vinculado'),
    	                        ('4','4-Particular'),('5','5-Otro'),('6','6-Víctima con afiliación al Régimen Contributivo'),
    	                        ('7','7-Víctima con afiliación al Régimen subsidiado'),('8','8-Víctima no asegurado (Vinculado)')]
    	                        ,string="Type User", related="insurer_id.type_user")
	code_assurance = fields.Char(string="Code Assurance", related="insurer_id.code_assurance")
	default_isure = fields.Boolean(string="Is default?")
	patient_insurer_id = fields.Many2one('doctor.patient', string="Assurance Patient")
	plan = fields.Many2one('doctor.insurer.plan', string="Plans")
	number_policy = fields.Char(string="Number policy")

	@api.onchange('insurer_id')
	def onchange_insurer_id(self):
		if self.insurer_id:
			domain = [('insurer_id', '=', self.insurer_id.id)]
			return {'domain': {'plan': domain}}

	# @api.onchange('default_isure')
	# def onchange_default_isure(self):
	# 	if self.default_isure:
	# 		patient_assurance_obj = self.env['patient.assurance'].search([('patient_insurer_id.name','=', self.patient_insurer_id.name)])
	# 		for patient_assurance_records in patient_assurance_obj:
	# 			if patient_assurance_records.id != self._origin.id:
	# 				print('ID que se convertira en FALSE')
	# 				print(patient_assurance_records)
	# 				print(patient_assurance_records.id)
	# 				print(patient_assurance_records.default_isure)
	# 				patient_assurance_records.update({'number_policy': '000'})


	# @api.onchange('default_isure')
	# def _isdone(self):
	# 	for record in self:
	# 		if record.default_isure:
	# 			if record.id != self._origin.id:
	# 				record.default_isure = False
