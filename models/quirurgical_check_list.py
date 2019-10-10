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

class ClinicaQuirurgicalCheckList(models.Model):
    _name = 'clinica.quirurgical.check.list'
    _description= 'Quirurgical Check List'  
    
    name = fields.Char(string='Name', copy=False)
    procedure_datetime = fields.Datetime(string='Procedure Date/Time', default=fields.Datetime.now)
    procedure_id = fields.Many2one('product.product', 'Procedure', ondelete='restrict')
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
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    technologist_id = fields.Many2one('doctor.professional', string='Surgical Technologists')
    nurse_id = fields.Many2one('doctor.professional', string='Auxiliary Nurse')
    
    #PRE-OPERATORY fields
    confirm_patient_name = fields.Selection([('yes','Yes'),('no', 'No')], string="Confirm Patient Name")
    confirm_bracelet_data = fields.Selection([('yes','Yes'),('no', 'No')], string="Bracelet data is verified: Name, Type and Identification Number, HR, Allergies")
    confirm_procedure = fields.Selection([('yes','Yes'),('no', 'No')], string="Confirm Procedure")
    surgical_concent_filled = fields.Selection([('yes','Yes'),('no', 'No')], string='Surgical informed consent fully filled out')
    pre_anesthetic_assessment_complete = fields.Selection([('yes','Yes'),('no', 'No')], string='Pre-anesthetic assessment and informed consent Anesthetic fully completed')
    removed_dental_aceesories = fields.Selection([('yes','Yes'),('no', 'No')], string='Removal of: Dental prostheses, jewelry, lenses, enamel, tampons, etc.')
    pre_surgical_lab_exams = fields.Selection([('yes','Yes'),('no', 'No')], string='Pre-surgical clinical laboratory exams.')
    patient_belongins_locked = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient's personal belongings are locked in the locker held by the relative")
    fasting_time_greater = fields.Selection([('yes','Yes'),('no', 'No')], string="Fasting time greater than 8 hours")
    flu_symptoms_enquired = fields.Selection([('yes','Yes'),('no', 'No')], string="I inquire about flu symptoms in the last week")
    allergic_enquired = fields.Selection([('yes','Yes'),('no', 'No')], string="Does the patient have allergies ?")
    allergic_text = fields.Text(string="Which?")
    enquired_proc_medication = fields.Selection([('yes','Yes'),('no', 'No')], string="Did the patient consume medications prior to the procedure?")
    investigated_drug_consumption = fields.Selection([('yes','Yes'),('no', 'No')], string="Did the patient consume alcoholic beverages and / or narcotic drugs prior to the procedure?")
    antiembolicas_stockings = fields.Selection([('yes','Yes'),('no', 'No')], string="Antiembolicas stockings")
    operational_site_marking = fields.Selection([('yes','Yes'),('no', 'No')], string="Operational site marking")
    special_preparation = fields.Selection([('yes','Yes'),('no', 'No')], string="Special preparations ?")
    special_preparations_text = fields.Text(string="Special preparations")
    
    #INTRA-OPERATORY fields
    recording_vital_signs = fields.Selection([('yes','Yes'),('no', 'No')], string="Taking and recording vital signs")
    antibiotic_prophylaxis = fields.Selection([('yes','Yes'),('no', 'No')], string="Antibiotic prophylaxis before surgery (which)")
    full_staff_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="Full staff is found inside the room to start the procedure")
    monitoring_induction_complete = fields.Selection([('yes','Yes'),('no', 'No')], string="Monitoring and induction is complete to start")
    monitor_indu_anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    is_scheduled = fields.Selection([('yes','Yes'),('no', 'No')], string="Is scheduled to ?")
    scheduled_surgeon_id = fields.Many2one('doctor.professional', string='Scheduled Surgeon')
    scheduled_patient_id = fields.Many2one('doctor.patient', 'Scheduled Patient')
    equipments_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="The requirements for equipment requested by you are in the room")
    equipments_room_surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    materials_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="Instrumentation the materials, medications and special supplies requested by the surgeon are in the room")
    equipments_in_order = fields.Selection([('yes','Yes'),('no', 'No')], string="Instrumentadora all the equipment is suitably sterile and in order")
    venous_pressure_working = fields.Selection([('yes','Yes'),('no', 'No')], string="Intermittent venous pressure working")
    supplies_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Additional items or supplies were delivered")
    pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Pay")
    proc_bill_pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Procedure bill is paid by")
    scheduled_nurse_id = fields.Many2one('doctor.professional', string='Surgery Assistant Nurse')
    
    #POST OPERATORY fields
    doctor_done_additionaly = fields.Selection([('yes','Yes'),('no', 'No')], string="Doctor something was done additionally or changed the procedure")
    sample_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Samples were delivered to the laboratory")
    sample_delivered_text = fields.Text(string="Delivered Samples Details")
    sample_delivered_pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Who pay the samples delivered to the laboratory")
    delivered_recovery_exam = fields.Selection([('yes','Yes'),('no', 'No')], string="Recovery exams are delivered")
    reported_disfunction_equip = fields.Selection([('yes','Yes'),('no', 'No')], string="I have reported the dysfunctional equipment or elements to the head of surgery")
    blood_returned = fields.Selection([('yes','Yes'),('no', 'No')], string="The requested blood was returned to the Blood Bank, which for any reason was not used")
    add_items_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Additional items delivered?")
    add_items_delivered_text = fields.Text(string="Were are the additional items delivered?")
    pay_add_items_delivered = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Who pay the aditional items delivered?")
    history_complete = fields.Selection([('yes','Yes'),('no', 'No')], string="History completed and signed")
    delivered_nurse_id = fields.Many2one('doctor.professional', string='Delivered Nurse')
    received_nurse_id = fields.Many2one('doctor.professional', string='Received Nurse')
    deliver_receive_time = fields.Datetime(string="Time")
    
    #RECOVERY fields
    recovery = fields.Text(string="Recovery")
    history_received = fields.Selection([('yes','Yes'),('no', 'No')], string="Full medical history is received")
    equipment_working = fields.Selection([('yes','Yes'),('no', 'No')], string="All equipment for monitoring and resuscitation of the patient working")
    informed_family = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient's family member is informed of their status and evolution")
    patient_out_with = fields.Selection([('nurse','Enfermera'),('family', 'Familiar')], string="The patient goes out with?")
    add_supplies = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient comes out with additional supplies")
    add_supplies_text = fields.Text(string="Additional supplies")

    observations = fields.Text(string="Observaciones")
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for check_list in self:
            if check_list.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(check_list.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    check_list.age_meassure_unit = '3'
                    check_list.age = int(date_diff.days)
                elif difference < 365:
                    check_list.age_meassure_unit = '2'
                    check_list.age = int(date_diff.months)
                else:
                    check_list.age_meassure_unit = '1'
                    check_list.age = int(date_diff.years)
                    
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
        for check_list in self:
            if check_list.age_meassure_unit == '3' and check_list.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if check_list.age > 17 and check_list.age_meassure_unit == '1' and check_list.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if check_list.age_meassure_unit in ['2','3'] and check_list.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if check_list.document_type == 'ms' and check_list.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if check_list.document_type == 'as' and check_list.age_meassure_unit == '1' and check_list.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
      
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('quirurgical.check.list') or '/'
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
        res = super(ClinicaQuirurgicalCheckList, self).create(vals)
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
        
        res = super(ClinicaQuirurgicalCheckList, self).write(vals)
        self._check_document_types()
        return res
    
        


    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


