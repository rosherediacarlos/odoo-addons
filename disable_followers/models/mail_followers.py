# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros  <cros@praxya.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailFollowers(models.Model):
    _inherit="mail.followers"

    @api.model
    def create(self, vals):
        if self.check_can_create(vals):
            super(MailFollowers,self).create(vals)
        
        
    
    def check_can_create(self, vals):
        disable_obj = self.env['mail.followers.disable']
        disable_ids = disable_obj.search(['model_id.model','ilike',vals.get('res_model')])
        
        #Si no tenemos
        if not bool(disable_ids):
            return True
        
        if any(disable_id.all_followers for disable_id in disable_ids):
            return False
        


