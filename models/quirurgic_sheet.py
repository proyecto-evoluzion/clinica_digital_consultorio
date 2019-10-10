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

import datetime as dt
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from odoo.exceptions import ValidationError
import html2text

class DoctorQuirurgicSheet(models.Model):
    _name = "doctor.quirurgic.sheet"
    _description= 'Doctor Quirurgic Sheet'      
    
    @api.model
    def _get_signature(self):
        user = self.env.user
        signature = html2text.html2text(user.signature)
        return signature
    
    name = fields.Char(string='Name', copy=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    procedure_date = fields.Date(string='Procedure Date')
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender', related='patient_id.sex')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    circulating_id = fields.Many2one('doctor.professional', string='Circulating')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    nurse_boss_id = fields.Many2one('doctor.professional', string='Nurse Boss')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    technologist_id = fields.Many2one('doctor.professional', string='Surgical Technologists')
    helper_id = fields.Many2one('doctor.professional', string='Surgical Helpers')
    procedure_scope = fields.Selection([('ambulatory','Ambulatorio'),('hospitable','Hospitalario'),
                                        ('emergency','Urgencias')], string='Scope of the Procedure', default='ambulatory')
    procedure_purpose = fields.Selection([('diagnosis','Diagnóstico'),('therapeutic','Terapéutico'),
                                        ('specific_protection','Protección específica'),('early_detection_general','Detección temprana de Enfermedad general'),
                                        ('early_detection_ocupational','Detección temprana de enfermedad laboral')], string='Purpose of the procedure', default='therapeutic')
    surgical_execution = fields.Selection([('single','Single or one-sided'),('multiple_same_diff','Multiple or bilateral, same route, different specialty'),
                                        ('multiple_same_same','Multiple or bilateral, same way, same specialty'), ('multiple_diff_diff','Multiple or bilateral, different way, different specialty'), ('multiple_diff_same','Multiple or bilateral, different way, same specialty')], string='Execution of the Surgical Act')
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis')
    tisue_sending_patologist = fields.Text(string='Tisue sending to patologist')
    procedure_id = fields.Many2one('product.product', string='Procedure')
    sign_stamp = fields.Text(string='Sign and médical stamp', default=_get_signature)
    user_id = fields.Many2one('res.users', string='Medical registry number', default=lambda self: self.env.user)
    description = fields.Text(string='Quirurgic Description')
    description_template_id = fields.Many2one('clinica.text.template', string='Template')
    
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    cigarate_daily = fields.Integer(string="Cigarettes / Day", related='patient_id.cigarate_daily')
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
                                  ('year','per Year')], string="Smoke Unit of Measure", default='day', related='patient_id.smoke_uom')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks", related='patient_id.is_alcoholic')
    alcohol_frequency = fields.Integer(string="Frequency", related='patient_id.alcohol_frequency')
    alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
                                              ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day', 
                                             related='patient_id.alcohol_frequency_uom')
    marijuana = fields.Boolean(string="Marijuana", related='patient_id.marijuana')
    cocaine = fields.Boolean(string="Cocaine", related='patient_id.cocaine')
    ecstasy = fields.Boolean(string="Ecstasy", related='patient_id.ecstasy')
    body_background_others = fields.Text(string="Body Background Others", related='patient_id.body_background_others')
    pharmacological = fields.Text(string="Pharmacological", related='patient_id.pharmacological')
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    abortion_number = fields.Integer(string="Number of Abortions", related='patient_id.abortion_number')
    last_birth_date = fields.Date(string="Date of Last Birth", related='patient_id.last_birth_date')
    last_menstruation_date = fields.Date(string="Date of Last Menstruation", related='patient_id.last_menstruation_date')
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for sheet in self:
            if sheet.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(sheet.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    sheet.age_meassure_unit = '3'
                    sheet.age = int(date_diff.days)
                elif difference < 365:
                    sheet.age_meassure_unit = '2'
                    sheet.age = int(date_diff.months)
                else:
                    sheet.age_meassure_unit = '1'
                    sheet.age = int(date_diff.years)
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh
            self.document_type = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_number_id(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
    
    @api.onchange('description_template_id')
    def onchange_description_template_id(self):
        if self.description_template_id:
            self.description = self.description_template_id.template_text
         
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
    def _check_birth_date(self, birth_date):
        warn_msg = '' 
        today_datetime = datetime.today()
        today_date = today_datetime.date()
        birth_date_format = datetime.strptime(birth_date, DF).date()
        date_difference = today_date - birth_date_format
        difference = int(date_difference.days)    
        if difference < 0: 
            warn_msg = _('Invalid birth date!')
        return warn_msg
    
    @api.multi
    def _check_document_types(self):
        for room in self:
            if room.age_meassure_unit == '3' and room.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if room.age > 17 and room.age_meassure_unit == '1' and room.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if room.age_meassure_unit in ['2','3'] and room.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if room.document_type == 'ms' and room.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if room.document_type == 'as' and room.age_meassure_unit == '1' and room.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
      
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('doctor.quirurgic.sheet') or '/'
        if vals.get('document_type', False) and vals['document_type'] in ['cc','ti']:
            numberid_integer = 0
            if vals.get('numberid_integer', False):
                numberid_integer = vals['numberid_integer']
            numberid = self._check_assign_numberid(numberid_integer)
            vals.update({'numberid': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(DoctorQuirurgicSheet, self).create(vals)
        res._check_document_types()
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('document_type', False) or 'numberid_integer' in  vals:
            if vals.get('document_type', False):
                document_type = vals['document_type']
            else:
                document_type = self.document_type
            if document_type in ['cc','ti']:
                if 'numberid_integer' in  vals:
                    numberid_integer = vals['numberid_integer']
                else:
                    numberid_integer = self.numberid_integer
                numberid = self._check_assign_numberid(numberid_integer)
                vals.update({'numberid': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        
        res = super(DoctorQuirurgicSheet, self).write(vals)
        self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.surgeon_id and self.surgeon_id.id or False,
            'default_view_model': 'quirurgic_sheet',
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
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:



