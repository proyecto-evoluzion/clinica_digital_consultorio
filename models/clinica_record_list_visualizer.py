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


class ClinicaRecordVisualizer(models.Model):
    _name = "clinica.record.list.visualizer"
    _order = 'id desc'
    _description = 'Clinica Record Visualizer'
    _rec_name = 'patient_id'
    
    patient_id = fields.Many2one('doctor.patient', 'Patient')
    one_record = fields.Boolean(string='Conservar último registro', default=True)
    pivot = fields.Boolean(string='pivote')
    doctor_id = fields.Many2one('doctor.professional', string='Doctor')
    start_period = fields.Datetime(string='Start Period')
    end_period = fields.Datetime(string='End Period')
    nurse_sheet_ids = fields.Many2many('clinica.nurse.sheet', 'nurse_sheet_visualizer_rel', 'visualizer_id', 'nurse_sheet_id', 
                                   string="Nurse Sheets", copy=False)
    quirurgic_sheet_ids = fields.Many2many('doctor.quirurgic.sheet', 'quirurgic_sheet_visualizer_rel', 'visualizer_id', 'quirurgic_sheet_id', 
                                   string="Quirurgic Sheets", copy=False)
    surgery_room_ids = fields.Many2many('doctor.waiting.room', 'surgery_visualizer_rel', 'visualizer_id', 'surgery_room_id', 
                                   string="Surgery Room Procedures", copy=False)
    waiting_room_ids = fields.Many2many('doctor.waiting.room', 'waiting_room_visualizer_rel', 'visualizer_id', 'waiting_room_id', 
                                   string="Waiting Room", copy=False)
    presurgical_record_ids = fields.Many2many('doctor.presurgical.record', 'presurgical_record_rel', 'visualizer_id', 'presurgical_record_id', 
                                   string="Pre-surgical Records", copy=False)
    anhestesic_registry_ids = fields.Many2many('clinica.anhestesic.registry', 'anhestesic_registry_visualizer_rel', 'visualizer_id', 'anhestesic_registry_id', 
                                   string="Anhestesic Registry", copy=False)
    plastic_surgery_ids = fields.Many2many('clinica.plastic.surgery', 'plastic_surgery_visualizer_rel', 'visualizer_id', 'plastic_surgery_id', 
                                   string="Plastic Surgery Sheets", copy=False)
    medical_evolution_ids = fields.Many2many('clinica.medical.evolution', 'medical_evolution_visualizer_rel', 'visualizer_id', 'medical_evolution_id', 
                                   string="Medical Orders and Evolution", copy=False)
    epicrisis_ids = fields.Many2many('doctor.epicrisis', 'epicrisis_visualizer_rel', 'visualizer_id', 'epicrisis_id', 
                                   string="Epicrisis", copy=False)
    prescription_ids = fields.Many2many('doctor.prescription', 'prescription_visualizer_rel', 'visualizer_id', 'prescription_id', 
                                   string="Prescription", copy=False)
    copy_prescription_ids = fields.Many2many('doctor.prescription', 'copy_prescription_visualizer_rel', 'copy_visualizer_id', 'copy_prescription_id', 
                                   string="Copy Prescription", copy=False)
    view_model = fields.Selection([('nurse_sheet','Nurse Sheet'),('quirurgic_sheet','Quirurgic Sheet'),
                                   ('surgery_room','Surgery Room Procedures'),('waiting_room','Waiting Room'),
                                   ('presurgical','Presurgical Record'),('anhestesic_registry','Anhestesic Registry'),
                                   ('plastic_surgery','Plastic Surgery'),('medical_evolution','Medical Evolution'),
                                   ('epicrisis','Epicrisis'),('prescription','Prescription'),('all','All')], string='View from model', default='all')
    
    
    def _get_nurse_sheet_ids(self, search_domain, doctor, start_period, end_period):
        nurse_sheet_ids = []
        nurse_search_domain = []
        nurse_search_domain.extend(search_domain)
        if start_period:
            nurse_search_domain.append(('procedure_date','>=',start_period))
        if end_period:
            nurse_search_domain.append(('procedure_date','<=',end_period))
        if doctor:
            nurse_search_domain.append(('room_id.surgeon_id','=',doctor.id))
            
        nurse_sheet_objs = self.env['clinica.nurse.sheet'].search(nurse_search_domain)
        if nurse_sheet_objs:
            nurse_sheet_ids = nurse_sheet_objs.ids
        return nurse_sheet_ids
    
    def _get_quirurgic_sheet_ids(self, search_domain, doctor, start_period, end_period):
        quirurgic_sheet_ids = []
        quirurgic_search_domain = []
        quirurgic_search_domain.extend(search_domain)
        if start_period:
            quirurgic_search_domain.append(('procedure_date','>=',start_period))
        if end_period:
            quirurgic_search_domain.append(('procedure_date','<=',end_period))
        if doctor:
            quirurgic_search_domain.append(('surgeon_id','=',doctor.id))
            
        quirurgic_sheet_objs = self.env['doctor.quirurgic.sheet'].search(quirurgic_search_domain)
        if quirurgic_sheet_objs:
            quirurgic_sheet_ids = quirurgic_sheet_objs.ids
        return quirurgic_sheet_ids
    
    def _get_surgery_room_ids(self, search_domain, doctor, start_period, end_period):
        surgery_room_ids = []
        waiting_room_ids = []
        surgery_room_domain = []
        waiting_room_domain = []
        surgery_search_domain = []
        waiting_room_objs = []
        surgery_room_objs = []
        surgery_search_domain.extend(search_domain)
        if start_period:
            surgery_search_domain.append(('procedure_date','>=',start_period))
            surgery_search_domain.append(('procedure_end_date','>=',start_period))
        if end_period:
            surgery_search_domain.append(('procedure_date','<=',end_period))
            surgery_search_domain.append(('procedure_end_date','<=',end_period))
        if doctor:
            surgery_search_domain.append(('surgeon_id','=',doctor.id))
        
        surgery_room_domain.extend(surgery_search_domain)
        waiting_room_domain.extend(surgery_search_domain)
        surgery_room_domain.append(('room_type','=','surgery'))
        waiting_room_domain.append(('room_type','=','waiting'))
        
        if self.view_model in ['surgery_room','all']:
            surgery_room_objs = self.env['doctor.waiting.room'].search(surgery_room_domain)
        if surgery_room_objs:
            surgery_room_ids = surgery_room_objs.ids
        if self.view_model in ['waiting_room','all']:
            waiting_room_objs = self.env['doctor.waiting.room'].search(waiting_room_domain)
        if waiting_room_objs:
            waiting_room_ids = waiting_room_objs.ids
        return surgery_room_ids,waiting_room_ids
    
    def _get_presurgical_record_ids(self, search_domain, doctor, start_period, end_period):
        presurgical_record_ids = []
        presurgical_search_domain = []
        presurgical_search_domain.extend(search_domain)
        if start_period:
            presurgical_search_domain.append(('date_attention','>=',start_period))
        if end_period:
            presurgical_search_domain.append(('date_attention','<=',end_period))
            
        presurgical_record_objs = self.env['doctor.presurgical.record'].search(presurgical_search_domain)
        if presurgical_record_objs:
            presurgical_record_ids = presurgical_record_objs.ids
        return presurgical_record_ids
    
    def _get_anhestesic_registry_ids(self, search_domain, doctor, start_period, end_period):
        anhestesic_registry_ids = []
        anhestesic_registry_search_domain = []
        anhestesic_registry_search_domain.extend(search_domain)
        if start_period:
            anhestesic_registry_search_domain.append(('intervention_date','>=',start_period))
        if end_period:
            anhestesic_registry_search_domain.append(('intervention_date','<=',end_period))
        if doctor:
            anhestesic_registry_search_domain.append(('surgeon_id','=',doctor.id))
            
        anhestesic_registry_record_objs = self.env['clinica.anhestesic.registry'].search(anhestesic_registry_search_domain)
        if anhestesic_registry_record_objs:
            anhestesic_registry_ids = anhestesic_registry_record_objs.ids
        return anhestesic_registry_ids
    
    def _get_plastic_surgery_ids(self, search_domain, doctor, start_period, end_period):
        plastic_surgery_ids = []
        plastic_surgery_search_domain = []
        plastic_surgery_search_domain.extend(search_domain)
        if start_period:
            plastic_surgery_search_domain.append(('date_attention','>=',start_period))
        if end_period:
            plastic_surgery_search_domain.append(('date_attention','<=',end_period))
            
        plastic_surgery_objs = self.env['clinica.plastic.surgery'].search(plastic_surgery_search_domain)
        if plastic_surgery_objs:
            plastic_surgery_ids = plastic_surgery_objs.ids
        return plastic_surgery_ids
    
    def _get_medical_evolution_ids(self, search_domain, doctor, start_period, end_period):
        medical_evolution_ids = []
        medical_evolution_search_domain = []
        medical_evolution_search_domain.extend(search_domain)
        if start_period:
            medical_evolution_search_domain.append(('procedure_date','>=',start_period))
        if end_period:
            medical_evolution_search_domain.append(('procedure_date','<=',end_period))
        if doctor:
            medical_evolution_search_domain.append(('surgeon_id','=',doctor.id))
            
        medical_evolution_objs = self.env['clinica.medical.evolution'].search(medical_evolution_search_domain)
        if medical_evolution_objs:
            medical_evolution_ids = medical_evolution_objs.ids
        return medical_evolution_ids
    
    def _get_epicrisis_ids(self, search_domain, doctor, start_period, end_period):
        epicrisis_ids = []
        epicrisis_search_domain = []
        epicrisis_search_domain.extend(search_domain)
        if start_period:
            epicrisis_search_domain.append(('patient_in_date','>=',start_period))
            epicrisis_search_domain.append(('patient_out_date','>=',start_period))
        if end_period:
            epicrisis_search_domain.append(('patient_in_date','<=',end_period))
            epicrisis_search_domain.append(('patient_out_date','<=',end_period))
            
        epicrisis_objs = self.env['doctor.epicrisis'].search(epicrisis_search_domain)
        if epicrisis_objs:
            epicrisis_ids = epicrisis_objs.ids
        return epicrisis_ids

    def _get_prescription_ids(self, search_domain, doctor, start_period, end_period):
        prescription_ids = []
        prescription_search_domain = []
        prescription_search_domain.extend(search_domain)
        if doctor:
            medical_evolution_search_domain.append(('doctor_id','=',doctor.id))
        if start_period:
            prescription_search_domain.append(('prescription_date','=',start_period))
            # prescription_search_domain.append(('patient_out_date','>=',start_period))
        # if end_period:
        #     prescription_search_domain.append(('patient_in_date','<=',end_period))
        #     prescription_search_domain.append(('patient_out_date','<=',end_period))
            
        prescription_objs = self.env['doctor.prescription'].search(prescription_search_domain)
        if prescription_objs:
            prescription_ids = prescription_objs.ids
        return prescription_ids
    
    @api.onchange('patient_id','start_period','end_period','doctor_id','view_model')
    def onchange_visualizer_filter(self):
        search_domain = []
        nurse_sheet_ids = []
        quirurgic_sheet_ids = []
        surgery_room_ids = []
        waiting_room_ids = []
        presurgical_record_ids = []
        anhestesic_registry_ids = []
        plastic_surgery_ids = []
        medical_evolution_ids = []
        epicrisis_ids = []
        prescription_ids = []
        if self.patient_id:
            search_domain.append(('patient_id','=',self.patient_id.id))
        if self.patient_id or self.doctor_id or self.start_period or self.end_period:
            if self.view_model in ['nurse_sheet','all']:
                nurse_sheet_ids = self._get_nurse_sheet_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['quirurgic_sheet','all']:
                quirurgic_sheet_ids = self._get_quirurgic_sheet_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['waiting_room','surgery_room','all']:
                surgery_room_ids,waiting_room_ids = self._get_surgery_room_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['presurgical','all']:
                presurgical_record_ids = self._get_presurgical_record_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['anhestesic_registry','all']:
                anhestesic_registry_ids = self._get_anhestesic_registry_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['plastic_surgery','all']:
                plastic_surgery_ids = self._get_plastic_surgery_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['medical_evolution','all']:
                medical_evolution_ids = self._get_medical_evolution_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['epicrisis','all']:
                epicrisis_ids = self._get_epicrisis_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            if self.view_model in ['prescription','all']:
                prescription_ids = self._get_prescription_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
            
        self.nurse_sheet_ids = nurse_sheet_ids
        self.quirurgic_sheet_ids = quirurgic_sheet_ids
        self.surgery_room_ids = surgery_room_ids
        self.waiting_room_ids = waiting_room_ids
        self.presurgical_record_ids = presurgical_record_ids
        self.anhestesic_registry_ids = anhestesic_registry_ids
        self.plastic_surgery_ids = plastic_surgery_ids
        self.medical_evolution_ids = medical_evolution_ids
        self.epicrisis_ids = epicrisis_ids
        self.prescription_ids = prescription_ids
        
    @api.multi
    def action_print_clinica_record_history(self):
        return self.env.ref('clinica_digital_consultorio.clinica_visualizer_report').report_action(self)

    @api.onchange('one_record')
    def onchange_recs(self):
        if self.view_model in ['prescription']:
            if self.one_record:
                cpy = 0
                self.copy_prescription_ids = [(6,0,self.prescription_ids.ids)]
                for cpy_rec in self.prescription_ids:
                    cpy = cpy_rec.id
                self.prescription_ids = [(6,0,[cpy])]
                self.pivot = True
            else:
                if self.pivot:
                    self.prescription_ids = [(6,0,self.copy_prescription_ids.ids)]
                    self.pivot = False
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:





