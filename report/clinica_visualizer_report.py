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


from odoo import api, models, _

class ClinicaVisualizerReport(models.AbstractModel):
    _name = 'report.clinica_digital_consultorio.visualizer_report'
    _description = 'Clinica Record History'
    
    @api.model
    def get_report_values(self, docids, data=None):
        visualizer_objs = self.env['clinica.record.list.visualizer'].browse(docids)
        clinica_record_dict = {'nurse_sheets': [], 'quirgic_sheets': [], 'surgery_rooms': [], 'waiting_rooms': [],
            'presurgical_records': [], 'anhestesic_registry': [], 'plastic_surgery': [], 'medical_evolution': [], 'epicrisis': [], 
            'prescription': []
            }
        for visualizer in visualizer_objs:
            clinica_record_dict.update({
                                    'nurse_sheets': visualizer.nurse_sheet_ids, 
                                    'quirgic_sheets': visualizer.quirurgic_sheet_ids, 
                                    'surgery_rooms': visualizer.surgery_room_ids, 
                                    'waiting_rooms': visualizer.waiting_room_ids,
                                    'presurgical_records': visualizer.presurgical_record_ids, 
                                    'anhestesic_registry': visualizer.anhestesic_registry_ids, 
                                    'plastic_surgery': visualizer.plastic_surgery_ids, 
                                    'medical_evolution': visualizer.medical_evolution_ids, 
                                    'epicrisis': visualizer.epicrisis_ids,
                                    'prescription': visualizer.prescription_ids})

        
        report_vals =  {
            'doc_ids': docids,
            'doc_model': 'clinica.record.list.visualizer',
            'docs': visualizer_objs,
            'clinica_records': clinica_record_dict,
        }
        return report_vals
        
        
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:









