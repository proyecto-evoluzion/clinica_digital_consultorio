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


class CrmLead(models.Model):
    _inherit = "crm.lead"

    
    @api.multi
    def doctor_appointment(self):

        self.ensure_one()
        action = self.env.ref('clinica_digital_consultorio.action_clinica_surgery_room_procedures').read()[0]
        future_partner = self.contact_name
        pivot = future_partner.find(" ")
        firstn = future_partner[:pivot]
        lastn = future_partner[pivot+1:]
        action['context'] = {
            'default_phone': self.phone,
            'default_name': self.name,
            'default_email_from': self.email_from,
            'default_email_from': self.email_from,
            'default_firstname': firstn,
            'default_lastname': lastn,
        }
        return action