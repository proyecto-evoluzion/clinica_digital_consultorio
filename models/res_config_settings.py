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

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    default_time_space = fields.Integer(string="Schedule Time Space in Minutes")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        default_time_space = params.get_param('clinica_digital_consultorio.default_time_space', default=5)
        res.update(
            default_time_space=float(default_time_space)
        )
        return res
    
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        default_time_space = float(self.default_time_space)
        self.env['ir.config_parameter'].sudo().set_param("clinica_digital_consultorio.default_time_space", default_time_space)
     
    
    

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:    
    
    