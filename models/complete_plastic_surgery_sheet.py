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
    _name = "complete.clinica.plastic.surgery"
    _rec_name = 'number'

    @api.depends('size','weight')
    def _comp_imc(self):
        if self.size != 0:
            for calc_imc in self:
                self.imc = self.weight / pow(self.size,2)

    @api.depends('imc')
    def _comp_igc(self):
        for igc in self:
            if igc.imc != 0:
                age = igc.patient_id.age
                sex = igc.patient_id.sex
                if sex == 'male':
                    sex = 1
                else:
                    sex = 0
                igc.igc = 1.39 * igc.imc + 0.16 * int(age) - 10.34 * int(sex) - 9

    def _default_system_review(self):
        system_rev_list = []
        system_rev_vals = {}
        system_review_obj = self.env['config.clinica.system.review'].search([])
        if system_review_obj:
            for system_rev in system_review_obj:
                system_rev_vals = {
                    'type_review': system_rev.type_review,
                    'system_review': system_rev.system_review
                }
                rec = self.env['clinica.system.review'].create(system_rev_vals)
                system_rev_list.append(rec.id)
        return [(6,0,system_rev_list)]

    def _default_physical_examination(self):
        physical_examination_list = []
        physical_examination_vals = {}
        physical_examination_obj = self.env['config.physical.examination'].search([])
        if physical_examination_obj:
            for physical_examination in physical_examination_obj:
                physical_examination_vals = {
                    'type_exam': physical_examination.type_exam,
                    'exam': physical_examination.exam
                }
                rec = self.env['physical.examination'].create(physical_examination_vals)
                physical_examination_list.append(rec.id)
        return [(6,0,physical_examination_list)]
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict')
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    type_id = fields.Selection([('fist_time','First Time'),('control','Control')], string='Consultation Type', default='fist_time')
    document_type = fields.Selection([('CC','CC - ID Document'),('CE','CE - Aliens Certificate'),('PA','PA - Passport'),('RC','RC - Civil Registry'),('TI','TI - Identity Card'),('AS','AS - Unidentified Adult'),('MS','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc_rips")
    numberid = fields.Char(string='Number ID', related='patient_id.name')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', related='patient_id.ref')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender', related="patient_id.sex")
    birth_date = fields.Date(string='Birth Date', related="patient_id.birth_date")
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    
    consultation_reason = fields.Text(string="Reason for Consultation")
    current_illness = fields.Text(string="Current illness")
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    toxic = fields.Text(string="Toxic")
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    gyneco_obst = fields.Text(string="Gyneco-Obstetricians")
    relatives = fields.Text(string="Relatives")
    others = fields.Text(string="Others")
    paraclinical = fields.Text(string="Paraclinical")
    therapies = fields.Text(string="Therapies")
    surgery = fields.Text(string="Surgery")

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
    code_diseases_id = fields.Many2one('doctor.diseases', string='Code')
 
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
    treatment = fields.Text(string="Paraclinical")
    confidential_notes = fields.Text(string="Confidential Notes")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    medical_recipe_template_id = fields.Many2one('clinica.text.template', string='Template')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    physical_examination_ids = fields.One2many('physical.examination', 'plastic_surgery_id', string="Physical Examination", default=_default_physical_examination)
    physical_examination_notes = fields.Text(string="Others")
    system_review_ids = fields.One2many('clinica.system.review', 'plastic_surgery_id', string="Systems Reviews", default=_default_system_review)
    system_review_notes = fields.Text(string="Others")
    background_ids = fields.One2many('clinica.patient.background', 'complete_format_id', string="Background")
    background_notes = fields.Text(string="Others")
    # diagnosis_ids = fields.One2many('doctor.diseases', 'complete_format_id', string="Diseases")
    doctor_id = fields.Many2one('doctor.professional', string='Professional')
    systolic_blood_pressure = fields.Float(string="Systolic blood pressure")
    diastolic_blood_pressure = fields.Float(string="Diastolic blood pressure")
    heart_rate = fields.Integer(string="Heart rate")
    breathing_frequency = fields.Integer(string="Breathing frequency")
    size = fields.Float(string="Size")
    weight = fields.Float(string="Weight")
    imc = fields.Float(string="IMC", compute=_comp_imc)
    analysis = fields.Text(string="Paraclinical")
    template_id = fields.Many2one('attention.quick.template', string='Template')
    sys_review_template_id = fields.Many2one('attention.quick.template', string='Plantilla', domain=[('type','=','15')])
    background_template_id = fields.Many2one('attention.quick.template', string='Plantilla', domain=[('type','=','5')])
    physical_template_id = fields.Many2one('attention.quick.template', string='Plantilla', domain=[('type','=','7')])
    analysis_template_id = fields.Many2one('attention.quick.template', string='Plantilla', domain=[('type','=','6')])
    treatment_template_id = fields.Many2one('attention.quick.template', string='Plantilla', domain=[('type','=','8')])
    prescription_id = fields.Many2one('doctor.prescription', string='Prescription')
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
    load_register = fields.Boolean(string='-', default=False)
    temp = fields.Float(string="Temperatura")
    igc = fields.Float(string="Indice de grasa corporal aproximado", compute=_comp_igc)
    pulse = fields.Integer(string="Pulsioximetría")
    diagnosis_ids = fields.One2many('consultorio.diagnosis.template', 'complete_format_id', string="Diagnóstico CIE10")
    consultation_purpose = fields.Selection([('01', 'Atención del parto puerperio'),('02', 'Atención del recién nacido'),
    										('03', 'Atención en planificación familiar'),('04', 'Detección de alteraciones de crecimiento y desarrollo del menor de diez años'),
    										('05', 'Detección de alteración del desarrollo joven'),('06', 'Detección de alteraciones del embarazo'),
    										('07', 'Detección de alteraciones del adulto'),('08', 'Detección de alteraciones de agudeza visual'),
    										('09', 'Detección de enfermedad profesional'),('10', 'No aplica')], string='Finalidad de la consulta')

    external_cause = fields.Selection([('01', 'Accidente de trabajo'),('02', 'Accidente de tránsito'),
    										('03', 'Accidente rábico'),('04', 'Accidente ofídico'),
    										('05', 'Otro tipo de accidente'),('06', 'Evento catastrófico'),
    										('07', 'Lesión por agresión'),('08', 'Lesión auto infligida'),
    										('09', 'Sospecha de maltrato físico'),('10', 'Sospecha de abuso sexual'),
    										('11', 'Sospecha de violencia sexual'),('12', 'Sospecha de maltrato emocional'),
    										('13', 'Enfermedad general'),('14', 'Enfermedad laboral'),
    										('15', 'Otra')], string='Causa Externa')

    background_type_ids = fields.Many2many('copy.background.type', string="Antecedentes")
    background_gynecology_ids = fields.One2many('background.gynecology','gynecology_id', string="Antecedente Ginecologico")
    #system_review_type_ids = fields.One2many('system.review.center','complete_format_id', string="Revision por sistemas")

    @api.multi
    def _set_prescription_form_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_complete_format_id' : self.id,
            'default_doctor_id' : self.doctor_id.id
        }
        return vals

    #Onchages para plantillas
    @api.onchange('sys_review_template_id')
    def onchange_sys_review_template_id(self):
        if self.sys_review_template_id:
            # self.system_review_ids = [(6,0,self.sys_review_template_id.system_review_ids.ids)]
            self.system_review_notes = self.sys_review_template_id.template_text

    @api.onchange('background_template_id')
    def onchange_background_template_id(self):
        if self.background_template_id:
            # self.background_type_ids = [(6,0,self.background_template_id.background_ids.ids)]
            self.background_notes = self.background_template_id.template_text

    @api.onchange('physical_template_id')
    def onchange_physical_template_id(self):
        if self.physical_template_id:
            # self.physical_examination_ids = [(6,0,self.physical_template_id.pysical_exam_ids.ids)]
            self.physical_examination_notes = self.physical_template_id.template_text
    
    @api.onchange('analysis_template_id')
    def onchange_analysis_id(self):
        if self.analysis_template_id:
            self.analysis = self.analysis_template_id.analisys

    @api.onchange('treatment_template_id')
    def onchange_treatment_id(self):
        if self.treatment_template_id:
            self.treatment  = self.treatment_template_id.treatment
            
    #Hasta aqui funcionalidad de plantillas
    

    @api.onchange('diagnosis_ids')
    def onchange_diagnosis_ids(self):
        for dignosis in self.diagnosis_ids:
            dignosis.update({'code': dignosis.diseases_id.code})
            dignosis.update({'name': dignosis.diseases_id.name})
            # dignosis.update({'type_diagnosis': dignosis.diseases_id.type_diagnosis})
            # dignosis.update({'state_diagnosis': dignosis.diseases_id.state_diagnosis})


    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'

    @api.multi
    def action_prescription(self):
        action = self.env.ref('clinica_digital_consultorio.action_doctor_prescription')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_prescription_form_default_values()
        prescription_ids = self.env['doctor.prescription'].search([('complete_format_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(prescription_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(prescription_ids.ids) + ")]"
        elif len(prescription_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.doctor_prescription_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = prescription_ids.id
        return result

    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    @api.onchange('patient_id')
    def onchange_consultation_reason(self):
        if self.patient_id:
            self.consultation_reason = self.patient_id.consultation_reason
            self.paraclinical = self.patient_id.paraclinical
            self.analysis = self.patient_id.analysis
            self.treatment = self.patient_id.treatment
            patient_background_obj = self.env['background.center'].search([('patient_id','=',self.patient_id.id)], limit=1)
            if patient_background_obj:
                self.background_type_ids = [(6,0,patient_background_obj.background_ids.ids)]
            else:
                create_list = []
                background_obj = self.env['background.type'].search([])
                for rec in background_obj:
                    copy_obj = self.env['copy.background.type'].create({'type_background': rec.id})
                    create_list.append(copy_obj.id)
                self.background_type_ids = [(6,0,create_list)]

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
         self.document_type = 'RC'
         #self.tdoc_rips = 'RC'
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
            if record.age_meassure_unit == '3' and record.document_type not in ['RC','MS']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if record.age > 17 and record.age_meassure_unit == '1' and record.document_type in ['RC','MS']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if record.age_meassure_unit in ['2','3'] and record.document_type in ['CC','AS','TI']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if record.document_type == 'MS' and record.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if record.document_type == 'AS' and record.age_meassure_unit == '1' and record.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
            
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('doctor.presurgical.record') or '/'
        if vals.get('document_type', False) and vals['document_type'] in ['CC','TI']:
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
        if res.prescription_id:
            res.prescription_id.name = res.number
            res.prescription_id.complete_format_id = res.id

        if res.consultation_reason:
            res.patient_id.consultation_reason = res.consultation_reason
        if res.analysis:
            res.patient_id.analysis = res.analysis
        if res.treatment:
            res.patient_id.treatment = res.treatment
        if res.paraclinical:
            paraclinical_vals = {
                'attention_id': res.id,
                'paraclinical': res.paraclinical,
                'date': res.date_attention,
                'patient_id': res.patient_id.id
            }
            res.env['background.paraclinical'].create(paraclinical_vals)
            paraclinical_obj = self.env['background.paraclinical'].search([('patient_id','=',res.patient_id.id)], order='id desc', limit=3)
            notes = ''
            for paraclinical_rec in paraclinical_obj:
                notes = notes + paraclinical_rec.date + '\r\n'
                notes = notes + paraclinical_rec.paraclinical + '\r\n'
            res.patient_id.paraclinical = notes
            

        if res.background_type_ids:
            bks_list =[]
            for bks in res.background_type_ids:
                bks_list.append(bks.id)
            bk_center_obj = self.env['background.center'].search([('patient_id','=',res.patient_id.id)],limit=1)
            if bk_center_obj:
                bk_center_obj.update({'background_ids': [(6,0,bks_list)]})
            else:
                self.env['background.center'].create({
                    'patient_id': res.patient_id.id,
                    'background_ids': [(6,0,bks_list)]
                    })

        res._check_document_types()
        return res
    
    
    @api.multi
    def write(self, vals):
        aux = 0
        if vals.get('document_type', False) or 'numberid_integer' in  vals:
            if vals.get('document_type', False):
                document_type = vals['document_type']
            else:
                document_type = self.document_type
            if document_type in ['CC','TI']:
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

        if vals.get('background_type_ids', False):
            aux += 1
        
        res = super(PlasticSurgerySheet, self).write(vals)
        self._check_document_types()

        if self.consultation_reason:
            self.patient_id.consultation_reason = self.consultation_reason
        if self.analysis:
            self.patient_id.analysis = self.analysis
        if self.treatment:
            self.patient_id.treatment = self.treatment
        if self.paraclinical:
            paraclinical_vals = {
                'attention_id': self.id,
                'paraclinical': self.paraclinical,
                'date': self.date_attention,
                'patient_id': self.patient_id.id
            }
            paraclinical_obj = self.env['background.paraclinical'].search([('attention_id','=',self.id)])
            if paraclinical_obj:
                paraclinical_obj.write(paraclinical_vals)
            paraclinical_obj = self.env['background.paraclinical'].search([('patient_id','=',self.patient_id.id)], order='id desc', limit=3)
            notes = ''
            for paraclinical_rec in paraclinical_obj:
                notes = notes + paraclinical_rec.date + '\r\n'
                notes = notes + paraclinical_rec.paraclinical + '\r\n'
            self.patient_id.paraclinical = notes

        if aux != 0:
            bks_list =[]
            for bks in self.background_type_ids:
                bks_list.append(bks.id)

            bk_center_obj = self.env['background.center'].search([('patient_id','=',self.patient_id.id)],limit=1)
            bk_center_obj.update({'background_ids': [(6,0,bks_list)]})

        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_view_model': 'complete_plastic_surgery',
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

class SystemsReviews(models.Model):
    _name = "clinica.system.review"

    plastic_surgery_id = fields.Many2one('complete.clinica.plastic.surgery', string='FCC')
    template_id = fields.Many2one('attention.quick.template', string='Template')
    type_review = fields.Char(string="Type Review")
    system_review = fields.Text(string="System Review")

class ConfigSystemsReviews(models.Model):
    _name = "config.clinica.system.review"
    _rec_name ="type_review"

    type_review = fields.Char(string="Type Review")
    system_review = fields.Text(string="System Review")

#class SystemReviewCenter(models.Model):
#    _name = "system.review.center"
#    _rec_name = "patient_id"
#
#    patient_id = fields.Many2one('doctor.patient',string="Paciente")
#    complete_format_id = fields.Many2one('complete.clinica.plastic.surgery',string="Atencion Clinica")
#    system_review_ids = fields.Many2many('system.review.type',string="Revision por sistemas") 

#    @api.multi
#    @api.onchange('patient_id')
#    def onchange_patient_id(self):
#        system_review_center_rec = self.env['system.review.center'].search([('patient_id', '=', self.patient_id.id)])
#        list_system = []
#        if system_review_center_rec:
#            list_system = system_review_center_rec.system_review_ids.ids
#            self.system_review_ids = [(6,0,list_system)]
#        else:
#            system_review_center_rec = self.env['system.review.type'].search([])
#            list_system = system_review_center_rec.ids
#            self.system_review_ids = [(6,0,list_system)]


# class PhysicalExaminationType(models.Model):
#     _name = "clinica.physical.item"

#     name = fields.Char(string="Name", required=True)
#     professional_id = fields.Many2one('doctor.professional', string='Professional')
#     active = fields.Boolean(string="Active", default="True")

class PhysicalExamination(models.Model):
    _name = "physical.examination"

    plastic_surgery_id = fields.Many2one('complete.clinica.plastic.surgery', string='FCC')
    type_exam = fields.Char(string="Type Physical Exam")
    exam = fields.Char(string="Exam")
    template_id = fields.Many2one('attention.quick.template', string='Template')

class ConfigPhysicalExamination(models.Model):
    _name = "config.physical.examination"
   
    type_exam = fields.Char(string="Type Physical Exam")
    exam = fields.Char(string="Exam")
