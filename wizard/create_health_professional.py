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

class CreateHealthProfessional(models.TransientModel):
    _name = "create.health.professional"
    _description = "Create Health Professional"
    
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    profession_type = fields.Selection([('plastic_surgeon','Plastic Surgeon'),('anesthesiologist','Anesthesiologist'),
                                        ('technologists','Surgical Technologists'),('helpers','Surgical Helpers')], 
                                       string='Profession Type', default='doctor')
    professional_product_ids = fields.Many2many('product.product', string='Products')
    
    
    @api.model
    def default_get(self, fields):
        res = super(CreateHealthProfessional, self).default_get(fields)
        ctx = dict(self.env.context) or {}
        partner_obj = self.env['res.partner'].browse(ctx.get('active_ids', False))
        for partner in partner_obj:
            res.update({
                'firstname': partner.x_name1 or '',
                'lastname': partner.x_name2 or '',
                'middlename': partner.x_lastname1 or '', 
                'surname': partner.x_lastname2 or '',
                'email': partner.email or '',
                'phone': partner.phone or '',
                })
        return res
    
    @api.multi
    def action_create_health_professional(self):
        products = []
        for product in self.professional_product_ids:
            products.append(product.id)
        ctx = dict(self.env.context) or {}
        partner_obj = self.env['res.partner'].browse(ctx.get('active_ids', False))
        health_professional_vals = {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'middlename': self.middlename,
            'surname': self.surname,
            'email': self.email or '',
            'phone': self.phone or '',
            'profession_type': self.profession_type,
            'product_ids': [(6,0, products)],
            'partner_id': partner_obj.id
            }
        doctor = self.env['doctor.professional'].create(health_professional_vals)
        partner_obj.professional_created = True
        return True
        
        
    
    
    
    
    