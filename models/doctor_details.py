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
from odoo import tools
import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError
import base64

class AssurancePlan(models.Model):
    _name = "doctor.insurer.plan"
    
    name = fields.Char(string='Plan')
    code = fields.Char(string='Plan Code')
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')
    
# class DoctorPatientOccupation(models.Model):
#     _name = "doctor.patient.occupation"
    
#     code = fields.Char(string='Code', copy=False)
#     name = fields.Char(string='Description')

class DoctorDiseases(models.Model):
    _name = "doctor.diseases"

    code = fields.Char('Code', size=4, required=False)
    name = fields.Char('Disease', size=256, required=False)
    type_diagnosis = fields.Selection([('principal','Principal'),
                             ('ralated','Relacionado')],default='principal', string='Type Diagnosis')
    state_diagnosis = fields.Selection([('diagnostic_impression','Impresión diagnóstica'),
                             ('confirm','Confirmado'),
                             ('recurrent','Recurrente')],default='diagnostic_impression', string='State Diagnosis')
    complete_format_id = fields.Many2one('complete.clinica.plastic.surgery', string='FCC')
    diseases_id = fields.Many2one('doctor.diseases', string='Code')

    _sql_constraints = [('code_uniq', 'unique (code)', 'The Medical Diseases code must be unique')]

    # @api.onchange('diseases_id')
    # def onchange_diseases_id(self):
    #     if self.diseases_id:
    #         self.code = self.diseases_id.code
    #         self.name = self.diseases_id.name
    
class AppointmentType(models.Model):
    _name = "clinica.appointment.type"
    
    name = fields.Char(string="Type")
    duration = fields.Float(string='Duration (in hours)')
    
    
class Doctor(models.Model):
    _name = "doctor.professional"
    _rec_name = "partner_id"
    
    tdoc = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    sex = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    partner_id = fields.Many2one('res.partner', copy=False, ondelete='restrict', string='Related Partner', 
                                    help='Partner-related data of doctor ')
    res_user_id = fields.Many2one('res.user', copy=False, ondelete='restrict', string='Related User', 
                                    help='User-related data of doctor ')
    profession_type = fields.Selection([('plastic_surgeon','Plastic Surgeon'),('anesthesiologist','Anesthesiologist'),
                                        ('technologists','Surgical Technologists'),('helpers','Surgical Helpers'),
                                        ('nurse','Nurse'),('otorhino','Otorhinolaryngologist')], 
                                       string='Profession Type', default='plastic_surgeon')
    product_ids = fields.Many2many('product.product', 'product_professional_rel', 'doctor_id', 'product_id', 
                                   string="Health Procedures", copy=False)
    medical_record = fields.Char(string='Medical record', required=True)

    @api.onchange('medical_record')
    def onchange_medical_record(self):
        if self.medical_record:
            is_mr = self.env['doctor.professional'].search([('medical_record','=',self.medical_record)])
            if is_mr:
                raise ValidationError(_('This medical record already exists in the system.'))    
    
    def _check_email(self, email):
        if not tools.single_email_re.match(email):
            raise ValidationError(_('Invalid Email ! Please enter a valid email address.'))
        else:
            return True
    
    @api.multi
    def _get_related_partner_vals(self, vals):
        ## code for updating partner with change in administrative data
        ## administrative data will not get updated with partner changes
        for data in self:
            partner_vals = {}
            if 'firstname' in vals or 'lastname' in vals or 'middlename' in vals or 'surname' in vals:
                firstname = data.firstname or ''
                lastname = data.lastname or ''
                middlename = data.middlename or ''
                surname = data.surname or ''
                if 'firstname' in vals:
                    firstname = vals.get('firstname', False) or ''
                    partner_vals.update({'x_name1': vals.get('firstname', False)})
                if 'lastname' in vals:
                    lastname = vals.get('lastname', False) or ''
                    partner_vals.update({'x_name2': vals.get('lastname', False)})
                if 'middlename' in vals:
                    middlename = vals.get('middlename', False) or ''
                    partner_vals.update({'x_lastname1': vals.get('middlename', False)})
                if 'surname' in vals:
                    surname = vals.get('surname', False) or ''
                    partner_vals.update({'x_lastname2': vals.get('surname', False)})
                nameList = [
                    firstname.strip(),
                    lastname.strip(),
                    middlename.strip(),
                    surname.strip()
                    ]
                formatedList = []
                name = ''
                for item in nameList:
                    if item is not '':
                        formatedList.append(item)
                    name = ' ' .join(formatedList).title()
                partner_vals.update({'name': name})
            if 'email' in vals:
                partner_vals.update({'email': vals.get('email', False)})
            if 'phone' in vals:
                partner_vals.update({'phone': vals.get('phone', False)})
            partner_vals.update({'professional_created': True})
            return partner_vals
      
    @api.model
    def create(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        res = super(Doctor, self).create(vals)
        if not res.partner_id:
            partner_vals = res._get_related_partner_vals(vals)
            partner_vals.update({'tdoc': 1})
            partner = self.env['res.partner'].create(partner_vals)
            res.partner_id = partner.id
        if not res.res_user_id:
            user_vals = {'active': True,
                            'login': vals.get('firstname').strip().lower()+'.'+vals.get('lastname').strip().lower(),
                            'password': 'admin',
                            'partner_id': partner.id,
                            'company_id': 1,
                            }
            user = self.env['res.users'].create(user_vals)
            res.res_user_id = user.id
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        res = super(Doctor, self).write(vals)
        if 'firstname' in vals or 'lastname' in vals or 'middlename' in vals or 'surname' in vals\
                 or 'email' in vals or 'phone' in vals :
            for doctor in self:
                if doctor.partner_id:
                    partner_vals = doctor._get_related_partner_vals(vals)
                    doctor.partner_id.write(partner_vals)
        return res
    

class DoctorAdministrativeData(models.Model):
    _name = "doctor.patient"
    _rec_name = 'patient_name'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('clinica_digital_consultorio', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    patient_name = fields.Char(string='Patient Name', size=60)
    name = fields.Char(string='Number ID')
    ref = fields.Integer(string='Number ID for TI or CC Documents')
    tdoc = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    photo = fields.Binary("Image", attachment=True, default=_default_image,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px", copy=False)
    photo_medium = fields.Binary("Medium-sized image", attachment=True, 
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.", copy=False)
    photo_small = fields.Binary("Small-sized image", attachment=True, 
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.", copy=False)
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    sex = fields.Selection([('male','Male'), ('female','Female')], string='Gender', required=True)
    birth_date = fields.Date(string='Birth Date')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    birth_country_id = fields.Many2one('res.country', string='Country of Birth', required=True, default=lambda self: self.env.ref('base.co'))
    provenance_country_id = fields.Many2one('res.country', string='Provenance', required=True, default=lambda self: self.env.ref('base.co'))
#    birth_city_id = fields.Many2one('res.country.state.city', string='Location/City/Town of Birth')
#     birth_district = fields.Char(string='Districts/localties/areas of Birth Place')
#     birth_neighborhood = fields.Char(string='Neighborhood of Birth Place')
#     birth_address = fields.Text(string="Address of Birth Place")
    residence_country_id = fields.Many2one('res.country', string='Residence Country', required=True, default=lambda self: self.env.ref('base.co'))
    residence_department_id = fields.Many2one('res.country.state', string='Residence Department/City', required=True, default=lambda self: self.env.ref('base.state_co_03'))
    residence_city_id = fields.Many2one('res.country.state.city', string='Residence Location/City/Town', required=True, default=lambda self: self.env.ref('clinica_digital_consultorio.res_country_state_city_co_03001'))
#    residence_district = fields.Char(string='Residence Districts/localties/areas', required=True)
#     residence_neighborhood = fields.Char(string='Residence Neighborhood')
    residence_address = fields.Text(string="Residence Address")
    civil_state = fields.Selection([('separated','Separada/o'),('single','Soltera/o'),('married','Casada/o'),
                                   ('free_union','Unión libre'),('widow','Viuda/o')], string='Civil Status')
#     beliefs = fields.Text(string="Beliefs")
    occupation =  fields.Char("Occupation")
#     profession_id = fields.Char(string='Profession')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')

    link_type = fields.Selection([('contributor','Contributor'),('beneficiary','Beneficiary')], string="Link Type")
#     mobile = fields.Char('Mobile Number')
    accompany_name = fields.Char("Name of the companion")
    accompany_relationship = fields.Selection([('mother','Mother'),('father','Father'),('grand_father','Grand Father'),
                                 ('grand_mother','Grand Mother'),('uncle','Uncle'),('aunt','Aunt'),
                                 ('friend','Friend'),('other','Other')], string="Accompany Person's Relationship")
    other_accompany_relationship = fields.Char(string="Other Accompany Person's Relationship")
    accompany_phone = fields.Char("Accompany Person's Phone Number")
    responsible_name = fields.Char("Responsible Person's Name")
    responsible_relationship = fields.Selection([('mother','Mother'),('father','Father'),('grand_father','Grand Father'),
                                     ('grand_mother','Grand Mother'),('uncle','Uncle'),('aunt','Aunt'),
                                     ('friend','Friend'),('other','Other')], string="Responsible Person's Relationship")
    other_responsible_relationship = fields.Char(string="Other Responsible Person's Relationship")
    responsible_phone = fields.Char("Responsible Person's Phone Number")
    copy_responsible_info = fields.Boolean(string="Is Also Responsible")

#     father_name = fields.Char(string="Father's Name")
#     father_occupation = fields.Char(string="Father's Occupation")
#     father_address = fields.Text(string="Father's Address")
#     father_phone = fields.Char(string="Father's Phone Number")
#     mother_name = fields.Char(string="Mother's Name")
#     mother_occupation = fields.Char(string="Mother's Occupation")
#     mother_address = fields.Text(string="Mother's Address")
#     mother_phone = fields.Char(string="Mother's Phone Number")
    user_type =  fields.Selection([('contributory','Contributory'),('subsidized','Subsidized'),('linked','Linked'),('particular','Particular'),('other','Other'),('victim_contributive','Victim - Contributive'),('victim_subsidized','Victim - Subsidized'),('victim_linked','Victim - Linked')], string="User Type", default='particular')
#     primary_payer =  fields.Selection([('private_user','Usuario Particular'),('eps','EPS'),
#                                        ('another_insurer','Otra Aseguradora'),('mixed','Pago Mixto')], string="Primary Payer")
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')
#     assurance_plan_id = fields.Many2one('assurance.plan', string='Assurer Plans')
#     other_assurance_partner_id = fields.Many2one('res.partner',string='Other Assurance Company')
#     other_assurance_plan_id = fields.Many2one('assurance.plan', string='Other Assurer Plans')
    doctor_id = fields.Many2one('doctor.professional', ondelete='restrict', string='Treating Doctor')
    partner_id = fields.Many2one('res.partner', copy=False, ondelete='restrict', string='Related Partner', 
                                    help='Partner-related data of administrative data ')
    consultation_reason = fields.Text(string="Reason for Consultation")
    pathological = fields.Text(string="Pathological")
    surgical = fields.Text(string="Surgical")
    smoke = fields.Boolean(string="Smoke")
    cigarate_daily = fields.Integer(string="Cigarettes")
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),
                                  ('month','per Month'), ('year','per Year')], string="Smoke Unit of Measure", default='day')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks")
    alcohol_frequency = fields.Integer(string="Frequency")
    alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
                                              ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day')
    marijuana = fields.Boolean(string="Marijuana")
    cocaine = fields.Boolean(string="Cocaine")
    ecstasy = fields.Boolean(string="Ecstasy")
    body_background_others = fields.Text(string="Body Background Others")
    pharmacological = fields.Text(string="Pharmacological")
    allergic = fields.Text(string="Allergic")
    pregnancy_number = fields.Integer(string="Number of Pregnancies")
    child_number = fields.Integer(string="Number of Children")
    abortion_number = fields.Integer(string="Number of Abortions")
    last_birth_date = fields.Date(string="Date of Last Birth")
    last_menstruation_date = fields.Date(string="Date of Last Menstruation")
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods")
    diabetes = fields.Boolean(string="Diabetes")
    hypertension = fields.Boolean(string="Hypertension")
    arthritis = fields.Boolean(string="Arthritis")
    thyroid_disease = fields.Boolean(string="Thyroid Disease")
    nurse_sheet_ids = fields.One2many('clinica.nurse.sheet', 'patient_id', string="Nurse Sheets", copy=False)
    quirurgic_sheet_ids = fields.One2many('doctor.quirurgic.sheet', 'patient_id', string="Quirurgic Sheets", copy=False)
    surgery_room_ids = fields.One2many('doctor.waiting.room', 'patient_id', string="Surgery Room Procedures", 
                                       copy=False, domain=[('room_type','=','surgery')])
    waiting_room_ids = fields.One2many('doctor.waiting.room', 'patient_id', string="Surgery Room Procedures", 
                                       copy=False, domain=[('room_type','=','waiting')])
    presurgical_record_ids = fields.One2many('doctor.presurgical.record', 'patient_id', string="Pre-surgical Records", 
                                             copy=False)
    anhestesic_registry_ids = fields.One2many('clinica.anhestesic.registry', 'patient_id', string="Anhestesic Registry", copy=False)
    plastic_surgery_ids = fields.One2many('clinica.plastic.surgery', 'patient_id', string="Plastic Surgery Sheets", copy=False)
    medical_evolution_ids = fields.One2many('clinica.medical.evolution', 'patient_id', string="Medical Orders and Evolution", copy=False)
    epicrisis_ids = fields.One2many('doctor.epicrisis', 'patient_id', string="Epicrisis", copy=False)
    
    
    # @api.multi
    # @api.depends('firstname', 'lastname', 'middlename', 'surname')
    # def _compute_patient_name(self):
    #     for data in self:
    #         firstname = data.firstname or ''
    #         lastname = data.lastname or ''
    #         middlename = data.middlename or ''
    #         surname = data.surname or ''
    #         nameList = [
    #             firstname.strip(),
    #             lastname.strip(),
    #             middlename.strip(),
    #             surname.strip()
    #             ]
    #         formatedList = []
    #         name = ''
    #         for item in nameList:
    #             if item is not '':
    #                 formatedList.append(item)
    #             name = ' ' .join(formatedList).title()
    #         data.patient_name = name
    
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
                    data.age_unit = '3'
                    data.age = int(date_diff.days)
                elif difference < 365:
                    data.age_unit = '2'
                    data.age = int(date_diff.months)
                else:
                    data.age_unit = '1'
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

    @api.onchange('birth_date','age_unit')
    def onchange_birth_date(self):
        if self.age_unit == '3':
            self.tdoc = 'rc'
        if self.birth_date:
            warn_msg = self._check_birth_date(self.birth_date)
            if warn_msg:
                warning = {
                        'title': _('Warning!'),
                        'message': warn_msg,
                    }
                return {'warning': warning}
            
    @api.onchange('copy_responsible_info')
    def onchange_copy_responsible_info(self):
        if self.copy_responsible_info:
            self.responsible_name = self.accompany_name
            self.responsible_relationship = self.accompany_relationship
            self.responsible_phone = self.accompany_phone
            self.other_responsible_relationship = self.other_accompany_relationship
        else:
            self.responsible_name = ''
            self.responsible_relationship = ''
            self.responsible_phone = ''
            self.other_responsible_relationship=''   
            
    @api.onchange('ref', 'tdoc')
    def onchange_ref(self):
        if self.ref:
            self.name = str(self.ref) 
        if self.tdoc and self.tdoc in ['cc','ti'] and self.ref == 0:
            self.name = str(0)
    
    def _check_email(self, email):
        if not tools.single_email_re.match(email):
            raise ValidationError(_('Invalid Email ! Please enter a valid email address.'))
        else:
            return True
        
    def _check_assign_numberid(self, ref):
        if ref == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(ref)
            return numberid
    
    @api.multi
    def _check_tdocs(self):
        for data in self:
            if data.age_unit == '3' and data.tdoc not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if data.age > 17 and data.age_unit == '1' and data.tdoc in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if data.age_unit in ['2','3'] and data.tdoc in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if data.tdoc == 'ms' and data.age_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if data.tdoc == 'as' and data.age_unit == '1' and data.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
        
    @api.multi
    def _get_related_partner_vals(self, vals):
        ## code for updating partner with change in administrative data
        ## administrative data will not get updated with partner changes
        for data in self:
            partner_vals = {}
            if 'firstname' in vals or 'lastname' in vals or 'middlename' in vals or 'surname' in vals:
                firstname = data.firstname or ''
                lastname = data.lastname or ''
                middlename = data.middlename or ''
                surname = data.surname or ''
                if 'firstname' in vals:
                    firstname = vals.get('firstname', False) or ''
                    partner_vals.update({'x_name1': vals.get('firstname', False)})
                if 'lastname' in vals:
                    lastname = vals.get('lastname', False) or ''
                    partner_vals.update({'x_name2': vals.get('lastname', False)})
                if 'middlename' in vals:
                    middlename = vals.get('middlename', False) or ''
                    partner_vals.update({'x_lastname1': vals.get('middlename', False)})
                if 'surname' in vals:
                    surname = vals.get('surname', False) or ''
                    partner_vals.update({'x_lastname2': vals.get('surname', False)})
                nameList = [
                    firstname.strip(),
                    lastname.strip(),
                    middlename.strip(),
                    surname.strip()
                    ]
                formatedList = []
                name = ''
                for item in nameList:
                    if item is not '':
                        formatedList.append(item)
                    name = ' ' .join(formatedList).title()
                partner_vals.update({'name': name})
            if 'birth_date' in vals:
                partner_vals.update({'xbirthday': vals.get('birth_date', False)})
            if 'email' in vals:
                partner_vals.update({'email': vals.get('email', False)})
            if 'phone' in vals:
                partner_vals.update({'phone': vals.get('phone', False)})
            if 'mobile' in vals:
                partner_vals.update({'mobile': vals.get('mobile', False)})
            if 'image' in vals:
                partner_vals.update({'image': vals.get('image', False)})
            if 'residence_district' in vals:
                partner_vals.update({'street2': vals.get('residence_district', False)})
            if 'residence_department_id' in vals:
                partner_vals.update({'state_id': vals.get('residence_department_id', False)})
            if 'residence_country_id' in vals:
                partner_vals.update({'country_id': vals.get('residence_country_id', False)})
            if 'residence_address' in vals:
                partner_vals.update({'street': vals.get('residence_address', False)})
            return partner_vals
    
    @api.model
    def create(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        if vals.get('tdoc', False) and vals['tdoc'] in ['cc','ti']:
            ref = 0
            if vals.get('ref', False):
                ref = vals['ref']
            numberid = self._check_assign_numberid(ref)
            vals.update({'name': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        tools.image_resize_images(vals)
        vals.update({'patient_name': "%s %s %s %s" % (vals['lastname'], vals['surname'] or '', vals['firstname'], vals['middlename'] or '')})
        res = super(DoctorAdministrativeData, self).create(vals)
        res._check_tdocs()
        partner_vals = res._get_related_partner_vals(vals)
        partner_vals.update({'tdoc': 1})
        partner = self.env['res.partner'].create(partner_vals)
        res.partner_id = partner.id 
        return res
        
    @api.multi
    def write(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        tools.image_resize_images(vals)
        if vals.get('tdoc', False) or vals.get('ref', False):
            if vals.get('tdoc', False):
                tdoc = vals['tdoc']
            else:
                tdoc = self.tdoc
            if tdoc in ['cc','ti']:
                if vals.get('ref', False):
                    ref = vals['ref']
                else:
                    ref = self.ref
                numberid = self._check_assign_numberid(ref)
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        tools.image_resize_images(vals)
        res = super(DoctorAdministrativeData, self).write(vals)
        self._check_tdocs()
        if 'firstname' in vals or 'lastname' in vals or 'middlename' in vals or 'surname' in vals\
                 or 'birth_date' in vals or 'email' in vals or 'phone' in vals or 'mobile' in vals or 'image' in vals \
                 or 'residence_district' in vals or 'residence_department_id' in vals or 'residence_country_id' in vals or 'residence_address' in vals:
            for data in self:
                if data.partner_id:
                    partner_vals = data._get_related_partner_vals(vals)
                    data.partner_id.write(partner_vals)
        return res

    _sql_constraints = [
        ('ref_tdoc_unique', 'unique(name,tdoc)', 'Error creating! This patient already exists in the system.')
    ]
    
    @api.multi
    def _set_clinica_form_default_values(self):
        return {'default_patient_id': self.id}
    
    @api.multi
    def action_view_surgery_room_procedures(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_surgery_room_procedures')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        ctx_vals = self._set_clinica_form_default_values()
        ctx_vals.update({'default_room_type': 'surgery'})
        result['context'] = ctx_vals
        room_proc_ids = self.env['doctor.waiting.room'].search([('room_type','=','surgery'),('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(room_proc_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(room_proc_ids.ids) + ")]"
        elif len(room_proc_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_waiting_room_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = room_proc_ids.id
        return result
    
    @api.multi
    def action_view_appointments(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_waiting_room')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        ctx_vals = self._set_clinica_form_default_values()
        ctx_vals.update({'default_room_type': 'waiting'})
        result['context'] = ctx_vals
        appointments = self.env['doctor.waiting.room'].search([('room_type','=','waiting'),('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(appointments) != 1:
            result['domain'] = "[('id', 'in', " + str(appointments.ids) + ")]"
        elif len(appointments) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_waiting_room_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = appointments.id
        return result
    
    @api.multi
    def action_view_nurse_sheet(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_nurse_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(nurse_sheet_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(nurse_sheet_ids.ids) + ")]"
        elif len(nurse_sheet_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.view_clinica_nurse_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = nurse_sheet_ids.id
        return result
    
    @api.multi
    def action_view_anhestesic_registry(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_anhestesic_registry')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        anhestesic_registry_ids = self.env['clinica.anhestesic.registry'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(anhestesic_registry_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(anhestesic_registry_ids.ids) + ")]"
        elif len(anhestesic_registry_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_anhestesic_registry_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = anhestesic_registry_ids.id
        return result  
          
    @api.multi
    def action_view_presurgical_record(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_presurgical_record')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        pre_surgical_ids = self.env['doctor.presurgical.record'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(pre_surgical_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(pre_surgical_ids.ids) + ")]"
        elif len(pre_surgical_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_presurgical_record_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pre_surgical_ids.id
        return result
    
    @api.multi
    def action_view_quirurgic_sheet(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_quirurgic_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        quirurgic_sheets = self.env['doctor.quirurgic.sheet'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(quirurgic_sheets) != 1:
            result['domain'] = "[('id', 'in', " + str(quirurgic_sheets.ids) + ")]"
        elif len(quirurgic_sheets) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_quirurgic_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = quirurgic_sheets.id
        return result
    
    @api.multi
    def action_view_quirurgical_check_list(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_quirurgical_check_list')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        quirurgic_check_lists = self.env['clinica.quirurgical.check.list'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(quirurgic_check_lists) != 1:
            result['domain'] = "[('id', 'in', " + str(quirurgic_check_lists.ids) + ")]"
        elif len(quirurgic_check_lists) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_quirurgical_check_list_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = quirurgic_check_lists.id
        return result
    
    @api.multi
    def action_view_post_anhestesic_care(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_post_anhestesic_care')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        post_anhestesic_care_ids = self.env['clinica.post.anhestesic.care'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(post_anhestesic_care_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(post_anhestesic_care_ids.ids) + ")]"
        elif len(post_anhestesic_care_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.view_clinica_post_anhestesic_care_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = post_anhestesic_care_ids.id
        return result
    
    @api.multi
    def action_view_plastic_surgery(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_plastic_surgery')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        plastic_surgery_ids = self.env['clinica.plastic.surgery'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(plastic_surgery_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(plastic_surgery_ids.ids) + ")]"
        elif len(plastic_surgery_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_plastic_surgery_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = plastic_surgery_ids.id
        return result
    
    @api.multi
    def action_view_medical_evolution(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_medical_evolution')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        evolution_ids = self.env['clinica.medical.evolution'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(evolution_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(evolution_ids.ids) + ")]"
        elif len(evolution_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_medical_evolution_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = evolution_ids.id
        return result
    
    @api.multi
    def action_view_epicrisis(self):
        action = self.env.ref('clinica_digital_consultorio.action_clinica_doctor_epicrisis')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        epicrisis_ids = self.env['doctor.epicrisis'].search([('patient_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(epicrisis_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(epicrisis_ids.ids) + ")]"
        elif len(epicrisis_ids) == 1:
            res = self.env.ref('clinica_digital_consultorio.clinica_doctor_epicrisis_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = epicrisis_ids.id
        return result
    

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


