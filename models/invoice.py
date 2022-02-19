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

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    copago = fields.Monetary(string="Copago")
    tdoc_rips = fields.Selection([('CC','CC - Cedula de ciudadania'),('CE','CE - Cedula de extranjeria'),
                                      ('PA','PA - Pasaporte'),('RC','RC - Registro civil'),('TI','TI - Tarjeta de identidad'),
                                      ('AS','AS - Adulto sin identificar'),('MS','MS - Menor sin identificar'),
                                      ('CD','CD - Carnet diplomatico'),('SC','SC - Salvaconducto'),
                                      ('PE','PE - Permiso de permanencia'),
                                      ('CN','CN - Certificado de nacido vivo')], string='Tipo Documento', related="partner_id.tdoc_rips", 
                                      readonly=True)
    number_identification = fields.Char(string="Número de Identificación", related="partner_id.number_identification", readonly=True)
    
    @api.multi
    def action_compute_procedure_time(self):
        for invoice in self:
            for line in invoice.invoice_line_ids:
                if line.sale_line_ids:
                    nurse_invc_line = self.env['nurse.sheet.invoice.procedures'].search([('sale_line_id','in',line.sale_line_ids.ids),
                                                                                         ('nurse_sheet_id.various_procedures','=',True)], limit=1)
                    if nurse_invc_line:
                        line_qty = nurse_invc_line.procedure_end_time - nurse_invc_line.procedure_start_time
                        line.quantity = line_qty
                    else:
                        sale_objs = self.env['sale.order'].search([('order_line','in',line.sale_line_ids.ids)])
                        if sale_objs:
                            room_obj = self.env['doctor.waiting.room'].search([('sale_order_id','in',sale_objs.ids)], limit=1)
                            anhestesic_registry = self.env['clinica.anhestesic.registry'].search([('room_id','=',room_obj.id)], limit=1)
                            if anhestesic_registry:
                                line_qty = anhestesic_registry.end_time - anhestesic_registry.anesthesia_start_time
                                line.quantity = line_qty


        
        
        