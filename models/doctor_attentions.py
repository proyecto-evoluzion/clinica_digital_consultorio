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

class PresurgicalRecord(models.Model):
    _name = "doctor.presurgical.record"
    _rec_name = 'number'
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict')
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender', related="patient_id.sex")
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    
    consultation_reason = fields.Text(string="Reason for Consultation")
    
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    relatives = fields.Text(string="Relatives")
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
    
    physical_sistolic_arteric_presure = fields.Integer(string="Sistolic Arteric Pressure")
    physical_diastolic_artery_presure = fields.Integer(string="Diastolic Artery Pressure")
    physical_fc = fields.Integer(string="FC")
    physical_fr = fields.Integer(string="FR")
    physical_weight = fields.Float(string="Weight", required=True)
    physical_size = fields.Float(string="Size", required=True)
    physical_body_mass_index = fields.Float(string="IMC (Body Mass Index)")
    physical_exam = fields.Text(string="Physical Exam")
    dental_prostheses = fields.Boolean(string='Dental Prostheses')
    prostheses_type = fields.Selection([('fixed','Fixed'),('removable','Removable')], string='Prostheses Type', default='fixed')
    prostheses_location = fields.Selection([('above','Above'),('below','Below')], string='Prostheses Location', default='above')
    
    paraclinical_exam_date = fields.Date(string="Paraclinical Exam Date")
    paraclinical_hb = fields.Float(string="HB")
    paraclinical_hto = fields.Float(string="Hto (Hematocrit)")
    paraclinical_leukocytes = fields.Float(string="Leukocytes")
    paraclinical_differential = fields.Text(string="Differential")
    paraclinical_vsg = fields.Integer(string="VSG")
    paraclinical_pt = fields.Float(string="PT")
    paraclinical_ptt = fields.Float(string="PTT")
    paraclinical_platelets = fields.Float(string="Platelets")
    paraclinical_tc = fields.Float(string="TC")
    paraclinical_glycemia = fields.Float(string="Glycemia")
    paraclinical_creatinine = fields.Float(string="Creatinine")
    paraclinical_albumin = fields.Float(string="Albumin")
    paraclinical_glob = fields.Text(string="Glob")
    paraclinical_ecg = fields.Text(string="E.C.G")
    paraclinical_rx_chest = fields.Text(string="Rx. Chest")
    paraclinical_others = fields.Text(string="Paraclinical Others")
    paraclinical_asa = fields.Selection([('1','ASA 1'),('2','ASA 2'),('3','ASA 3'),
                                         ('4','ASA 4'), ('5','ASA 5') ], string="A.S.A")
    paraclinical_goldman = fields.Selection([('class_1','Class I'),
                                             ('class_2','Class II'),
                                             ('class_3','Class III'),
                                             ('class_4','Class IV')],
                                            string="GOLDMAN", default='class_1')
    mallampati_scale = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='Mallampati Scale')
    suitable_surgery = fields.Boolean(string='Suitable for Surgery')
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    other_diseases = fields.Boolean(string="Other Diseases")
    disease2_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease3_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease_type = fields.Selection([('principal', 'Principal'),('related', 'Relacionado')], string='Kind')
    disease_state = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    disease_state2 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    disease_state3 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    process_id = fields.Many2one('product.product', string='Process', ondelete='restrict')
    plan_analysis = fields.Text(string="Plan, Analysis and Conduct")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    medical_recipe_template_id = fields.Many2one('clinica.text.template', string='Template')
    mallampati_scale = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='Mallampati Scale')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    @api.onchange('patient_id')
    def onchange_consultation_reason(self):
        if self.patient_id:
            self.consultation_reason = self.patient_id.consultation_reason

    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for data in self:
            if data.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(data.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    data.age_meassure_unit = '3'
                    data.age = int(date_diff.days)
                elif difference < 365:
                    data.age_meassure_unit = '2'
                    data.age = int(date_diff.months)
                else:
                    data.age_meassure_unit = '1'
                    data.age = int(date_diff.years)

            
    @api.onchange('medical_recipe_template_id')
    def onchange_medical_recipe_template_id(self):
        if self.medical_recipe_template_id:
            self.medical_recipe = self.medical_recipe_template_id.template_text
            
            
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('doctor.presurgical.record') or '/'
        res = super(PresurgicalRecord, self).create(vals)
#         res._check_document_types()
        return res
    
    
    @api.multi
    def write(self, vals):        
        res = super(PresurgicalRecord, self).write(vals)
#         self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_view_model': 'presurgical',
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
    
    @api.onchange('physical_size')
    def onchange_imc(self):
        if self.physical_size and self.physical_weight:
            self.physical_body_mass_index = float(self.physical_weight/(self.physical_size/100)**2)
    
    
    