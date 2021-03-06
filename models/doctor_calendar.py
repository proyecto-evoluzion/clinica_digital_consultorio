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
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from odoo.exceptions import ValidationError,AccessError, UserError, RedirectWarning, Warning
import xmlrpc.client
from lxml import etree
# from xmlrpc import client as xmlrpclib

class ClinicaSurgeryRoom(models.Model):
    _name = "clinica.surgery.room"
    
    name = fields.Char(string='Description')

class DoctorSchedule(models.Model):
    _name = "doctor.schedule"
    _description= 'Doctor Schedule'
    _rec_name = 'professional_id'
    _order = 'id desc'
    
    professional_id = fields.Many2one('doctor.professional', string='Doctor')
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now, copy=False)
    duration = fields.Float(string='Duration (in hours)')
    end_date = fields.Datetime(string='End Date', copy=False)
    room_ids = fields.One2many('doctor.waiting.room', 'schedule_id', string='Waiting Rooms/Appointments', copy=False)
    time_allocation_ids = fields.One2many('doctor.schedule.time.allocation', 'schedule_id', string='Time Allocations', copy=False)
    
    @api.onchange('start_date','duration')
    def onchange_start_date_duration(self):
        if self.start_date:
            start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.end_date = start_date + timedelta(hours=self.duration)
            
    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
            end_date = datetime.strptime(self.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
            duration = end_date - start_date
            hour_diff = duration.total_seconds()/3600
            self.duration = hour_diff
            
    @api.multi
    def allocate_schedule_time(self):
        time_space = self.env['ir.config_parameter'].sudo().get_param('clinica_digital_consultorio.default_time_space')
        time_space = int(time_space)
        start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        final_time = start_date + timedelta(hours=self.duration)  
        time_space_start = start_date
        allocation_vals_list = []
        while time_space_start < final_time:
            end_time = time_space_start + timedelta(minutes=time_space)  
            if end_time > final_time:
                end_time = final_time
            alloc_vals = {
                'start_time': time_space_start,
                'end_time': end_time
                }
            allocation_vals_list.append((0, 0, alloc_vals))
            time_space_start = end_time
            
        return allocation_vals_list
        
        
    @api.model
    def create(self, vals):
        res = super(DoctorSchedule, self).create(vals)
        res.time_allocation_ids = res.allocate_schedule_time()
        return res
    
    @api.multi
    def write(self, vals):
        res = super(DoctorSchedule, self).write(vals)
        if 'duration' in vals or 'start_date' in vals or 'end_date' in vals:
            assigned_allocations = self.env['doctor.schedule.time.allocation'].search([('schedule_id','=',self.id),
                                                                                       ('state','=','assigned')])
            if assigned_allocations:
                raise ValidationError(_("You cannot change schedule time! There are already assigned appointments for this schedule."))
            self.time_allocation_ids.unlink()
            self.time_allocation_ids = self.allocate_schedule_time()
        return res
    
    @api.multi
    def get_next_appointment_start_date(self):
        assigned_allocs = self.env['doctor.schedule.time.allocation'].search([('schedule_id','=',self.id),('state','=','assigned')])
        next_appointment_start = datetime.now()
        if not assigned_allocs:
            next_appointment_start = self.start_date
            return next_appointment_start
        for alloc in self.time_allocation_ids:
            if alloc.state != 'assigned':
                next_appointment_start = alloc.start_time
                break
        return next_appointment_start
            
    
    @api.multi
    def action_create_appointment(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_waiting_room')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = {'default_room_type': 'waiting', 'default_schedule_id': self.id}
        
        #choose the view_mode accordingly
        res = self.env.ref('clinica_digital_consultorio.clinica_waiting_room_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result
            
class ScheduleTimeAllocation(models.Model):
    _name = "doctor.schedule.time.allocation"
    _order = 'start_time'
    
    schedule_id = fields.Many2one('doctor.schedule', string="Schedule", ondelete='cascade')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    state = fields.Selection([('not_assigned','Not Assigned'),('assigned','Assigned')],
                              string='Status', copy=False, default='not_assigned')

class DoctorWaitingRoom(models.Model):
    _name = "doctor.waiting.room"
    _description= 'Doctor Waiting Room'


    @api.multi
    def api_connect(self):
        # Parametros de conexion:
        db = "evolutionmedicalcenter"
        # db = "copiaevolutionmedicalcenter"
        username ="api@test.com"
        password = "api.test"
        url = 'https://evolutionmedicalcenter.clinicadigital.net'
        # url = 'http://copiaevolutionmedicalcenter.clinicadigital.net'

        # Apuntando al EndPoint de Odoo
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        plastic_surgery_obj = self.env['clinica.plastic.surgery'].search([('room_id','=', self.id)], limit=1)

        # Read() Existing Records
        ids = []
        flag = 0
        if plastic_surgery_obj.patient_id:
            # Se busca paciente
            if plastic_surgery_obj.patient_id.ref:
                ids = models.execute_kw(db, uid, password,
                    'doctor.patient', 'search',
                    [[['ref', '=', plastic_surgery_obj.patient_id.ref]]],
                    {'limit': 1})
            else:
                ids = models.execute_kw(db, uid, password,
                    'doctor.patient', 'search',
                    [[['name', '=', plastic_surgery_obj.patient_id.name]]],
                    {'limit': 1})

        if len(ids) > 0:
            patient_id = self.env['doctor.patient'].search([('id','=',ids[0])], limit=1)
            patient_id = patient_id.id
        else:
            patient_id = models.execute_kw(db, uid, password, 'doctor.patient', 'create', [{
                'tdoc_rips': plastic_surgery_obj.patient_id.tdoc_rips or '',
                'ref': plastic_surgery_obj.patient_id.ref or '',
                'name': plastic_surgery_obj.patient_id.name or '',
                'lastname': plastic_surgery_obj.patient_id.lastname or '',
                'firstname': plastic_surgery_obj.patient_id.firstname or '',
                'middlename': plastic_surgery_obj.patient_id.middlename or '',
                'surname': plastic_surgery_obj.patient_id.surname or '',
                'sex': plastic_surgery_obj.patient_id.sex or '',
                'birth_date': plastic_surgery_obj.patient_id.birth_date or '',
                'blood_type': plastic_surgery_obj.patient_id.blood_type or '',
                'blood_rh': plastic_surgery_obj.patient_id.blood_rh or '',
                'user_type': plastic_surgery_obj.patient_id.user_type or '',
                'email': plastic_surgery_obj.patient_id.email or '',
                'phone': plastic_surgery_obj.patient_id.phone or '',
                'link_type': plastic_surgery_obj.patient_id.link_type or '',
                'residence_address': plastic_surgery_obj.patient_id.residence_address or '',
                'birth_country_id': plastic_surgery_obj.patient_id.birth_country_id.id or False,
                'residence_country_id': plastic_surgery_obj.patient_id.residence_country_id.id or False,
                'provenance_country_id': plastic_surgery_obj.patient_id.provenance_country_id.id or False,
                'residence_address': plastic_surgery_obj.patient_id.residence_address or '',
                'civil_state': plastic_surgery_obj.patient_id.civil_state or '',
                'occupation': plastic_surgery_obj.patient_id.occupation or '',
                'responsible_name': plastic_surgery_obj.patient_id.responsible_name or '',
                'responsible_relationship': plastic_surgery_obj.patient_id.responsible_relationship or '',
                'responsible_relationship': plastic_surgery_obj.patient_id.responsible_relationship or '',
                'responsible_phone': plastic_surgery_obj.patient_id.responsible_phone or '',
                'accompany_relationship': plastic_surgery_obj.patient_id.accompany_relationship or '',
                'accompany_relationship': plastic_surgery_obj.patient_id.accompany_relationship or '',
                'accompany_phone': plastic_surgery_obj.patient_id.accompany_phone or '',
                'consultation_reason': plastic_surgery_obj.patient_id.consultation_reason or '',
                'doctor_id': 2,
                }])

            # Write()

            if plastic_surgery_obj.patient_id.residence_department_id:
                residence_department_id = models.execute_kw(db, uid, password,
                    'res.country.state', 'search',
                    [[['name', '=', plastic_surgery_obj.patient_id.residence_department_id.name],['country_id', '=',49]]],
                    {'limit': 1})
            else:
                residence_department_id = False

            if plastic_surgery_obj.patient_id.residence_city_id:
                residence_city_id = models.execute_kw(db, uid, password,
                    'res.country.state.city', 'search',
                    [[['name', '=', plastic_surgery_obj.patient_id.residence_city_id.name]]],
                    {'limit': 1})
            else:
                residence_city_id = False

            if plastic_surgery_obj.patient_id.insurer_id:
                insurer_id = models.execute_kw(db, uid, password,
                    'res.partner', 'search',
                    [[['xidentification', '=', plastic_surgery_obj.patient_id.insurer_id.xidentification]]],
                    {'limit': 1})
            else:
                insurer_id = False

            update = models.execute_kw(db, uid, password, 'doctor.patient', 'write', [[patient_id], {
                'residence_city_id': residence_city_id[0] or False,
                'residence_department_id': residence_department_id[0] or False,
                'insurer_id': insurer_id[0] or False,
                }])

        # Read() Disease
        if plastic_surgery_obj.disease_id:
            disease = models.execute_kw(db, uid, password,
                'doctor.diseases', 'search',
                [[['code', '=', plastic_surgery_obj.disease_id.code]]],
                {'limit': 1})
            disease = disease[0]
        else:
            disease = False

        # Create()
        partner_id = models.execute_kw(db, uid, password, 'clinica.plastic.surgery', 'create', [{
            'date_attention': plastic_surgery_obj.date_attention,
            # 'number': "Dr. Antonio Salgado / "+ plastic_surgery_obj.number or '',
            'patient_id': patient_id,
            # 'document_type': .document_type,
            'consultation_reason': plastic_surgery_obj.consultation_reason or '',
            'pathological': plastic_surgery_obj.pathological or '',
            'surgical': plastic_surgery_obj.surgical or '',
            'toxic': plastic_surgery_obj.toxic or '',
            'allergic': plastic_surgery_obj.allergic or '',
            'gyneco_obst': plastic_surgery_obj.gyneco_obst or '',
            'pharmacological': plastic_surgery_obj.pharmacological or '',
            'gestations': plastic_surgery_obj.gestations or '',
            'births': plastic_surgery_obj.births or '',
            'cesarean': plastic_surgery_obj.cesarean or '',
            'abortion_number': plastic_surgery_obj.abortion_number or '',
            'last_menstruation_date': plastic_surgery_obj.last_menstruation_date or '',
            'last_birth_date': plastic_surgery_obj.last_birth_date or '',
            'mature_promoting_factor': plastic_surgery_obj.mature_promoting_factor or '',
            'relatives': plastic_surgery_obj.relatives or '',
            'others': plastic_surgery_obj.others or '',
            'size': plastic_surgery_obj.size or 0.00,
            'weight': plastic_surgery_obj.weight or 0.00,
            'imc': plastic_surgery_obj.imc or 0.00,
            'heart_rate': plastic_surgery_obj.heart_rate or 0,
            'breathing_frequency': plastic_surgery_obj.breathing_frequency or 0,
            'systolic_blood_pressure': plastic_surgery_obj.systolic_blood_pressure or 0.00,
            'diastolic_blood_pressure': plastic_surgery_obj.diastolic_blood_pressure or 0.00,
            # 'physical_examination_ids': plastic_surgery_obj.physical_examination_ids,
            'physical_exam': plastic_surgery_obj.physical_exam or '',
            'disease_id': disease,
            'disease_state': plastic_surgery_obj.disease_state or '',
            'treatment': plastic_surgery_obj.treatment or '',
            # 'prescription_id': plastic_surgery_obj.prescription_id.id,
            'doctor_id': 2,
            # 'professional_id': 2,
            }])
        self.send_hc = True

    def _default_config_value(self):
        config_value = self.env['res.config.settings'].sudo().default_get('multiple_format')
        return config_value['multiple_format']

    def _default_config_value2(self):
        config_value = self.env['res.config.settings'].sudo().default_get('emc_api')
        return config_value['emc_api']

    
    name = fields.Char(string='Name', copy=False)
    room_type = fields.Selection([('surgery','Surgery Room'),('waiting','Waiting Room')], string='Room Type')
    surgery_room_id = fields.Many2one('clinica.surgery.room', string='Surgery Room', copy=False)
    schedule_id = fields.Many2one('doctor.schedule', string='Schedule', copy=False)
    procedure_date = fields.Datetime(string='Procedure Date', default=fields.Datetime.now, copy=False)
    procedure_end_date = fields.Datetime(string='Procedure End Date', copy=False)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    email_from = fields.Char(string='Email From CRM')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    phone = fields.Char(string='Telephone')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], string='Type of Anesthesia')
    circulating_id = fields.Many2one('doctor.professional', string='Circulating')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    nurse_boss_id = fields.Many2one('doctor.professional', string='Nurse Boss')
    technologist_id = fields.Many2one('doctor.professional', string='Surgical Technologists')
    procedure = fields.Text(string='Procedure')
    notes = fields.Text(string='Observations or Notes')
    programmer_id = fields.Many2one('res.users', string='Programmer', default=lambda self: self.env.user)
    procedure_ids = fields.One2many('doctor.waiting.room.procedures', 'room_id', string='Helath Procedures', copy=False)
    state = fields.Selection([('new','New'),('confirmed','Confirmed'),('ordered','SO Created')], 
                                        string='Status', default='new')
    patient_state = fields.Selection([('dated','Citado'),('attended','Atendido'),('not_attended','No asistio'),('in_room','En sala de espera'),('retired','Se retiró')], 
                                        string='Estado paciente', default='dated')
    nurse_sheet_created = fields.Boolean(string='Nurse Sheet Created', compute='_compute_nurse_sheet_creation')
    anhestesic_registry_created = fields.Boolean(string='Anhestesic Registry Created', compute='_compute_anhestesic_registry_creation')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    cigarate_daily = fields.Integer(string="Cigarettes / Day", related='patient_id.cigarate_daily')
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
                                  ('year','per Year')], string="Smoke Unit of Measure", default='day', related='patient_id.smoke_uom')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks", related='patient_id.is_alcoholic')
    send_hc = fields.Boolean(string="HC sended?")
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
    assigned_professional_ids = fields.Many2many('doctor.professional', 'waiting_room_professional_rel', 'room_id', 'professional_id', 
                                                string="Responsible Professionals", copy=False)
    from_surgery_procedure = fields.Boolean(string='Created from Surgery Room Procedure', copy=False)
    user_type =  fields.Selection([('contributory','Contributory'),('subsidized','Subsidized'),('linked','Linked'),
                                   ('particular','Particular'),('other','Other'),('victim_contributive','Victim - Contributive'),
                                   ('victim_subsidized','Victim - Subsidized'),('victim_linked','Victim - Linked')], string="User Type", default='particular')
    appointment_type_id = fields.Many2one('clinica.appointment.type', string='Appointment Type')
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')
    assurance_plan_id = fields.Many2one('doctor.insurer.plan', string='Assurer Plan')
    schedule_allocation_id = fields.Many2one('doctor.schedule.time.allocation', string='Schedule Time Allocation')
    attention_format_ids = fields.Many2many('att.format', 
                                   string="Attention Formats", copy=False)
    emc_api = fields.Boolean(string='EMC API Connect?', default=_default_config_value2)
    multiple_format = fields.Boolean(string='Multiple Formats?', default=_default_config_value)
    is_simple_format = fields.Boolean(string='Is Simple Format?')
    is_complete_format = fields.Boolean(string='Is Complete Format?')
    
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for room in self:
            if room.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(room.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    room.age_meassure_unit = '3'
                    room.age = int(date_diff.days)
                elif difference < 365:
                    room.age_meassure_unit = '2'
                    room.age = int(date_diff.months)
                else:
                    room.age_meassure_unit = '1'
                    room.age = int(date_diff.years)
                    
    @api.multi
    def _compute_nurse_sheet_creation(self):
        for room in self:
            nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',room.id)])
            if nurse_sheet_ids:
                room.nurse_sheet_created = True           
                     
    @api.multi
    def _compute_anhestesic_registry_creation(self):
        for room in self:
            anhestesic_registry_ids = self.env['clinica.anhestesic.registry'].search([('room_id','=',room.id)])
            if anhestesic_registry_ids:
                room.anhestesic_registry_created = True

    @api.onchange('surgeon_id')
    def onchange_surgeon_id(self):
        if self.surgeon_id.multiple_format:
            att_format = []
            for att_f in self.surgeon_id.attention_format_ids:
                att_format.append(att_f.id)
                if att_f.type == 'simple':
                    self.update({'is_simple_format': True})
                if att_f.type == 'complete':
                    self.update({'is_complete_format': True})
            self.update({'attention_format_ids': [(6,0,att_format)]})


        if self.room_type and self.room_type == 'surgery':
            self.from_surgery_procedure = True
        else:
            self.from_surgery_procedure = False
                
    @api.onchange('room_type')
    def onchange_room_type(self):
        if self.room_type and self.room_type == 'surgery':
            self.from_surgery_procedure = True
        else:
            self.from_surgery_procedure = False
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.phone = self.patient_id.phone
            self.document_type = self.patient_id.tdoc_rips
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            
    @api.onchange('schedule_id')
    def onchange_schedule_id(self):
        if self.schedule_id:
            self.surgeon_id = self.schedule_id.professional_id and self.schedule_id.professional_id.id or False
            if self.schedule_id.time_allocation_ids:
                start_date = self.schedule_id.get_next_appointment_start_date()
                self.procedure_date = start_date
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
            
    @api.onchange('procedure_date','appointment_type_id')
    def onchange_procedure_date(self):
        if self.procedure_date:
            if self.appointment_type_id:
                duration = self.appointment_type_id.duration
            else: 
                duration = 4
            procedure_date = datetime.strptime(self.procedure_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.procedure_end_date = procedure_date + timedelta(hours=duration)
    
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
      
    @api.multi
    def _validate_surgeon_room(self):
        for room in self:
            if self.surgeon_id:
                start_date = self.procedure_date
                end_date = self.procedure_end_date
                if end_date and start_date:
                    if end_date <= start_date:
                        raise ValidationError(_("End date should be greater than start date!"))
                    start_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<=',start_date),
                                                ('procedure_end_date','>',start_date),
                                                ])
                    if len(start_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    end_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<',end_date),
                                                ('procedure_end_date','>=',end_date),
                                                ])
                    if len(end_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    
                    overlap_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','>=',start_date),
                                                ('procedure_end_date','<=',end_date),
                                                ])
                    if len(overlap_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
    
    @api.multi
    def _validate_surgery_room_alocation(self):   
        for room in self:  
            start_date = self.procedure_date
            end_date = self.procedure_end_date
            if end_date and start_date:
                start_time_between_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','<=',start_date),
                                            ('procedure_end_date','>',start_date),
                                            ])
                if len(start_time_between_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
                end_time_between_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','<',end_date),
                                            ('procedure_end_date','>=',end_date),
                                            ])
                if len(end_time_between_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
                
                overlap_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','>=',start_date),
                                            ('procedure_end_date','<=',end_date),
                                            ])
                if len(overlap_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
    
    @api.multi
    def _add_assigned_professionals(self,):
        professional_ids = []
        if self.surgeon_id:
            professional_ids.append(self.surgeon_id.id)
        if self.anesthesiologist_id:
            professional_ids.append(self.anesthesiologist_id.id)
        if self.circulating_id:
            professional_ids.append(self.circulating_id.id)
        if self.nurse_boss_id:
            professional_ids.append(self.nurse_boss_id.id)
        if self.technologist_id:
            professional_ids.append(self.technologist_id.id)
        self.assigned_professional_ids = [(6, 0, professional_ids)]
        
    @api.multi
    def _allocate_in_schedule_time(self):
        schedule_alloc_pool = self.env['doctor.schedule.time.allocation']
        time_space_domain = [('schedule_id','=',self.schedule_id.id),'|', '|',
                             '&', ('start_time','>=', self.procedure_date), ('end_time','<=', self.procedure_end_date),
                             '&', ('start_time','<=', self.procedure_date), ('end_time','<=', self.procedure_date),
                             '&', ('start_time','<=', self.procedure_end_date), ('end_time','>=', self.procedure_end_date),]
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','>=', self.procedure_date), ('end_time','<=', self.procedure_end_date),
                             ('start_time','!=', self.procedure_end_date), ('end_time','!=', self.procedure_date)]
        between_allocation_objs = schedule_alloc_pool.search(time_space_domain)
        
        if between_allocation_objs:
            between_allocation_objs.unlink()
            
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_date), ('end_time','>', self.procedure_date)]
        start_overlap_allocation_objs =  schedule_alloc_pool.search(time_space_domain, limit=1)
        if start_overlap_allocation_objs:
            start_overlap_allocation_objs.end_time = self.procedure_date
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_end_date), ('end_time','>', self.procedure_end_date)]
        end_overlap_allocation_objs = schedule_alloc_pool.search(time_space_domain, limit=1)
        if end_overlap_allocation_objs:
            end_overlap_allocation_objs.start_time = self.procedure_end_date
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_date), ('end_time','>', self.procedure_end_date)]
        start_end_overlap_objs = schedule_alloc_pool.search(time_space_domain, limit=1)
        if start_end_overlap_objs:
            aloc_end = start_end_overlap_objs.end_time
            start_end_overlap_objs.end_time = self.procedure_date
            end_new_alloc = schedule_alloc_pool.create({'start_time': self.procedure_end_date,
                                                        'end_time': self.aloc_end,
                                                        'schedule_id': self.schedule_id.id})
        
        new_allocation_vals = {
            'start_time': self.procedure_date,
            'end_time': self.procedure_end_date,
            'patient_id': self.patient_id and self.patient_id.id or False,
            'state': 'assigned',
            'schedule_id': self.schedule_id.id
            }
        new_allocation = schedule_alloc_pool.create(new_allocation_vals)
        self.schedule_allocation_id = new_allocation.id
        
    @api.multi
    def _reallocate_schedule_time(self, vals):
        new_start = vals.get('procedure_date', False)
        new_end = vals.get('procedure_end_date', False)
        schedule_alloc_pool = self.env['doctor.schedule.time.allocation']
        if new_start:
            time_space_domain = [('schedule_id','=',self.schedule_id.id), ('state','!=', 'assigned'),
                                 ('start_time','<=',new_start),('end_time','>=', new_start)]
            before_start_allocs = schedule_alloc_pool.search(time_space_domain, order='start_time desc', limit=1)
            if before_start_allocs and before_start_allocs.id != self.schedule_allocation_id.id:
                before_start_allocs.end_time = new_start
            self.schedule_allocation_id.start_time = new_start
        if new_end:
            time_space_domain = [('schedule_id','=',self.schedule_id.id),('state','!=', 'assigned'),
                                 ('start_time','<=',new_end), ('end_time','>=', new_end)]
            after_start_allocs = schedule_alloc_pool.search(time_space_domain, order='start_time desc', limit=1)
            if after_start_allocs and after_start_allocs.id != self.schedule_allocation_id.id:
                after_start_allocs.start_time = new_end
            self.schedule_allocation_id.end_time = new_end
            
        
        if new_start:
            start_time = new_start
        else:
            start_time = self.procedure_date
        if new_end:
            end_time = new_end
        else:
            end_time = self.procedure_end_date
            
        time_space_domain = [('schedule_id','=',self.schedule_id.id), ('state','!=', 'assigned'),
                             ('start_time','>=',start_time),('end_time','<=',end_time)]
            
        between_allocs = schedule_alloc_pool.search(time_space_domain)
        if between_allocs:
            between_allocs.unlink()
            
    
    @api.model
    def create(self, vals):
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            vals['name'] = self.env['ir.sequence'].next_by_code('doctor.surgery.room.procedure') or '/'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('doctor.waiting.room') or '/'
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
        if not vals.get('procedure_ids', False):
            warn_msg = _('Error! Plase add at least one procedure.')
            raise ValidationError(warn_msg)
        
        res = super(DoctorWaitingRoom, self).create(vals)
        res._check_document_types()
        res._validate_surgeon_room()
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            if vals.get('surgery_room_id', False):
                res._validate_surgery_room_alocation()
                
        if vals.get('surgeon_id', False) or vals.get('anesthesiologist_id', False) \
            or vals.get('circulating_id', False) or vals.get('nurse_boss_id', False) \
            or vals.get('technologist_id', False):
            res._add_assigned_professionals()
        if vals.get('schedule_id', False):
            res._allocate_in_schedule_time()
        res.state = 'confirmed'
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
            
        if vals.get('procedure_date', False) or vals.get('procedure_end_date', False):
            if self.schedule_id and self.schedule_allocation_id:
                self._reallocate_schedule_time(vals)
                
        res = super(DoctorWaitingRoom, self).write(vals)
        self._check_document_types()
        self._validate_surgeon_room()
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            if vals.get('surgery_room_id', False):
                self._validate_surgery_room_alocation()
        if 'surgeon_id' in vals or 'anesthesiologist_id' in vals or 'circulating_id' in vals \
            or 'nurse_boss_id' in vals or 'technologist_id' in vals:
            self._add_assigned_professionals()
        return res
    
    @api.multi
    def action_confirm(self):
        for room in self:
            room.state = 'confirmed'
            
    @api.multi
    def _set_nurse_sheet_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_room_id' : self.id,
        }
        anhestesic_registry = self.env['clinica.anhestesic.registry'].search([('room_id','=',self.id)], limit=1)
        if anhestesic_registry:
            vals.update({'default_anhestesic_registry_id': anhestesic_registry.id})
        if self.sale_order_id and self.sale_order_id.picking_ids:
            procedure_list = []
            for picking in self.sale_order_id.picking_ids:
                for move in picking.move_lines:
                    procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
                                                'product_uom_qty': move.product_uom_qty,
                                                'quantity_done': move.quantity_done,
                                                'move_id': move.id}))
            if procedure_list:
                vals.update({'default_procedure_ids': procedure_list})
        return vals
            
    @api.multi
    def action_view_nurse_sheet(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_nurse_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_nurse_sheet_values()
        nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(nurse_sheet_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(nurse_sheet_ids.ids) + ")]"
        elif len(nurse_sheet_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.view_clinica_nurse_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = nurse_sheet_ids.id
        return result
    
    @api.multi
    def _create_so(self):
        for room in self:
            so_vals = {
                    'partner_id': room.patient_id and room.patient_id.partner_id and room.patient_id.partner_id.id or False
                }
            sale_order = self.env['sale.order'].create(so_vals)
            for procedure in room.procedure_ids:
                so_line_vals = {
                    'product_id': procedure.product_id and procedure.product_id.id or False,
                    'product_uom_qty': procedure.quantity,
                    'order_id': sale_order.id,
                    }
                self.env['sale.order.line'].create(so_line_vals)
        return sale_order
    
    @api.multi
    def action_create_so(self):
        for room in self:
            room.sale_order_id = room._create_so().id
            room.state = 'ordered'
        return self.action_view_sale_order()
            
    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        res = self.env.ref('sale.view_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.sale_order_id.id
        return result
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.surgeon_id and self.surgeon_id.id or False,
            }
        if self.room_type == 'waiting':
            vals.update({'default_view_model': 'waiting_room'})
        elif self.room_type == 'surgery':
            vals.update({'default_view_model': 'surgery_room'})
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
        
    @api.multi
    def _set_clinica_form_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_room_id' : self.id
        }
        return vals

    @api.multi
    def action_not_attended(self):
        for record in self:
            record.patient_state = 'not_attended'

    @api.multi
    def action_arrive(self):
        for record in self:
            record.patient_state = 'in_room'

    @api.multi
    def action_retired(self):
        for record in self:
            record.patient_state = 'retired'
    
    @api.multi
    def action_view_plastic_surgery(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_plastic_surgery')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        plastic_surgery_ids = self.env['clinica.plastic.surgery'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(plastic_surgery_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(plastic_surgery_ids.ids) + ")]"
        elif len(plastic_surgery_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_plastic_surgery_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = plastic_surgery_ids.id
        return result

    @api.multi
    def action_view_complete_plastic_surgery(self):
        action = self.env.ref('clinica_digital_consultorio.complete_action_clinica_plastic_surgery')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        plastic_surgery_ids = self.env['complete.clinica.plastic.surgery'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(plastic_surgery_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(plastic_surgery_ids.ids) + ")]"
        elif len(plastic_surgery_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.complete_clinica_plastic_surgery_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = plastic_surgery_ids.id
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        res = super(DoctorWaitingRoom, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        simple_format = ''
        complete_format = ''
        doc = etree.XML(res['arch'])
        format_obj = self.env['att.format'].search([])
        for format_name in format_obj:
            if format_name.type == 'simple':
                simple_format = format_name.name
            if format_name.type == 'complete':
                complete_format = format_name.name
        for node in doc.xpath("//button[@name='action_view_plastic_surgery']"):
            node.set('string',  simple_format)
        for node in doc.xpath("//button[@name='action_view_complete_plastic_surgery']"):
            node.set('string',  complete_format)
        res['arch'] = etree.tostring(doc)
        return res
    

class DoctorWaitingRoomProcedures(models.Model):
    _name = "doctor.waiting.room.procedures"
    
    room_id = fields.Many2one('doctor.waiting.room', string='Waiting Room', copy=False)
    product_id = fields.Many2one('product.product', string='Health Procedure')
    quantity = fields.Float(string='Quantity', default=1)
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    
    @api.onchange('surgeon_id','anesthesiologist_id')
    def onchange_surgeon_anesthesiologist(self):
        product_list = []
        domain = {}
        if self.surgeon_id and self.surgeon_id.product_ids:
            product_list += self.surgeon_id.product_ids.ids
        if self.anesthesiologist_id and self.anesthesiologist_id.product_ids:
            product_list += self.anesthesiologist_id.product_ids.ids
        domain.update({'product_id': [('id','in',product_list)]})
        return {'domain': domain}
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

