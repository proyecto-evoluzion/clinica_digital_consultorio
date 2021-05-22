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


class AttentionQuickTemplate(models.Model):
    _name = "attention.quick.template"
    _order = 'id desc'
    _description = 'Attention Template'
    _rec_name = 'name'
    
    name = fields.Char(string='Template Name')
    template_text = fields.Text(string='Template Text')
    type = fields.Selection([('1','Recomendación'),
                             ('2','Informe de Certificado'),
                             ('3','Prescripción'),
                             ('4','Sintomas'),
                             ('5','Antecedentes'),
                             ('6','Análisis'),
                             ('7','Exámen Físisco'),
                             ('8','Conducta'),
                             ('9','Auxiliar de Enfermería'),
                             ('10','Hallazgos positivos de exámen físico'),
                             ('11','Descripción física'),('behaivor in consultation','Comportamiento en consulta'),
                             ('12 ','Estrategias de evaluacion'),
                             ('13','Plan de intervención'),
                             ('14','Otras prescripciones'),
                             ('15','Revisiones por sistema')
                             ], string='Template Type')
    active = fields.Boolean(string="active", default=True)
    user_id = fields.Many2one('res.users', string="User")
    system_review_ids = fields.One2many('clinica.system.review', 'template_id', string="Revisiones por sistema")
    background_ids = fields.Many2many('copy.background.type', string="Antecedentes")
    
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:




