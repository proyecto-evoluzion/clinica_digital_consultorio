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
    _name = "clinica.plastic.surgery"
    _rec_name = 'number'

    @api.depends('size','weight')
    def _comp_imc(self):
        for imc in self:
            if imc.size != 0:
                imc.imc = imc.weight / pow(imc.size,2)    
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict')
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    type_id = fields.Selection([('fist_time','First Time'),('control','Control')], string='Consultation Type', default='fist_time')
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc")
    numberid = fields.Char(string='Number ID', related='patient_id.name')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', related='patient_id.ref')
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
    
    consultation_reason = fields.Text(string="Reason for Consultation", related="patient_id.consultation_reason")
    this_consultation_reason = fields.Text(string="Motivo de Consulta")
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    toxic = fields.Text(string="Toxic")
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    gyneco_obst = fields.Text(string="Gyneco-Obstetricians")
    relatives = fields.Text(string="Relatives")
    others = fields.Text(string="Others")

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
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    
    gestations = fields.Integer(string="G", help="Gestations")
    births = fields.Integer(string="B",  help="Births")
    cesarean = fields.Integer(string="C", help="Cesarean")
    abortion_number = fields.Integer(string="A", related='patient_id.abortion_number', help="Abortions")
    last_menstruation_date = fields.Date(string="LMD", related='patient_id.last_menstruation_date', help="Last menstruation date")
    last_birth_date = fields.Date(string="LBD", related='patient_id.last_birth_date', help="Last birth date")
    mature_promoting_factor = fields.Char(string="MPF",  help="Mature Promoting Factor")

    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    
    physical_sistolic_arteric_presure = fields.Integer(string="Sistolic Arteric Pressure")
    physical_diastolic_artery_presure = fields.Integer(string="Diastolic Artery Pressure")
    physical_fc = fields.Integer(string="FC")
    physical_fr = fields.Integer(string="FR")
    physical_weight = fields.Float(string="Weight")
    physical_size = fields.Float(string="Size")
    physical_body_mass_index = fields.Float(string="IMC (Body Mass Index)")
    physical_exam = fields.Text(string="Physical Exam Observations")
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
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
    treatment = fields.Text(string="Treatment")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    medical_recipe_template_id = fields.Many2one('clinica.text.template', string='Template')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    physical_examination_ids = fields.One2many('clinica.physical.examination', 'plastic_surgery_id', string="Physical Examination")
    doctor_id = fields.Many2one('doctor.professional', string='Professional')
    prescription_id = fields.Many2one('doctor.prescription', string='Prescription')
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')    
    systolic_blood_pressure = fields.Float(string="Systolic blood pressure")
    diastolic_blood_pressure = fields.Float(string="Diastolic blood pressure")
    heart_rate = fields.Integer(string="Heart rate")
    breathing_frequency = fields.Integer(string="Breathing frequency")    
    size = fields.Float(string="Size")
    weight = fields.Float(string="Weight")
    imc = fields.Float(string="IMC", compute=_comp_imc)
    load_register = fields.Boolean(string='-', default=False)

    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'    
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    @api.onchange('patient_id')
    def onchange_this_consultation_reason(self):
        if self.patient_id:
            self.this_consultation_reason = self.patient_id.consultation_reason

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
            
    @api.onchange('physical_size')
    def onchange_imc(self):
        if self.physical_size and self.physical_weight:
            self.physical_body_mass_index = float(self.physical_weight/(self.physical_size/100)**2)

    @api.onchange('birth_date','age_meassure_unit')
    def onchange_birth_date(self):
        if self.age_meassure_unit == '3':
            self.document_type = 'rc'
        if self.birth_date:
            warn_msg = self._check_birth_date(self.birth_date)
            if warn_msg:
                warning = {
                        'title': _('Warning!'),
                        'message': warn_msg,
                    }
                return {'warning': warning}
            
    @api.onchange('numberid_integer', 'document_type')
    def onchange_numberid_integer(self):
        if self.numberid_integer:
            self.numberid = str(self.numberid_integer) 
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer == 0:
            self.numberid = str(0)
            
    @api.onchange('medical_recipe_template_id')
    def onchange_medical_recipe_template_id(self):
        if self.medical_recipe_template_id:
            self.medical_recipe = self.medical_recipe_template_id.template_text
            
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
    @api.multi
    def _check_document_types(self):
        for record in self:
            if record.age_meassure_unit == '3' and record.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if record.age > 17 and record.age_meassure_unit == '1' and record.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if record.age_meassure_unit in ['2','3'] and record.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if record.document_type == 'ms' and record.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if record.document_type == 'as' and record.age_meassure_unit == '1' and record.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
            
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('doctor.presurgical.record') or '/'
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

        ctx = self._context
        if ctx.get('uid'):
            create_uid = self.env['res.users'].search([('id','=',ctx.get('uid'))])
            professional_obj = self.env['doctor.professional'].search([('res_user_id','=',create_uid.id)])
            if professional_obj:
                vals['doctor_id'] = professional_obj.id
        
        res = super(PlasticSurgerySheet, self).create(vals)
        if res.room_id:
            res.room_id.patient_state = 'attended'
        if res.this_consultation_reason:
            res.consultation_reason = res.this_consultation_reason
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
        
        res = super(PlasticSurgerySheet, self).write(vals)
        self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_view_model': 'plastic_surgery',
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

class PhysicalExamination(models.Model):
    _name = "clinica.physical.examination"

    plastic_surgery_id = fields.Many2one('clinica.plastic.surgery', string='Plastic Surgery')
    element = fields.Many2one('clinica.physical.item', string='Tipo Exámen Físico')
    physical_examination = fields.Char(string="Exámen Físico")

class PhysicalExaminationType(models.Model):
    _name = "clinica.physical.item"

    name = fields.Char(string="Name", required=True)
    professional_id = fields.Many2one('doctor.professional', string='Professional')
    active = fields.Boolean(string="Active", default="True")
    
    
    
    