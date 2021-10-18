# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailFollowersDisable(models.Model):
    _name="mail.followers.disable"

    
    model_id = fields.Many2one(
        string='Modelo',
        comodel_name='ir.model',
    )
    
    all_followers = fields.Boolean(
        string='Deshabilitar todos',
    )

    field_id = fields.Many2one(
        string='Campo relacionado',
        comodel_name='model.name',
        help="Campo relacionado con el modelo de contactos (res.partner)"
    )
    
    @api.onchange('model_id')
    @api.depends('model_id')
    def compute_field_domain(self):
        for model in self:
            if bool(self.model_id):
                domain = {'field_id': [('model_id','=',self.model_id.id)]}
                return {'domain': domain}

    def search_field(self):
        print('a')
        self.env.cr.execute("""select *
            from ir_model_fields
            where model_id  = 202
            and relation ilike 'res.partner'
            and ttype ilike 'many2one'
            and related is null
            order by id
            limit 1
            """
        return False
        