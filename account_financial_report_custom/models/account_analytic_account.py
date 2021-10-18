# -*- coding: utf-8 -*-
# (c) 2021 Carlos Ros <cros@praxya.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    def get_account_children(self):
        childs = self.mapped('child_ids')
        if childs.mapped('child_ids'):
            childs |= childs.mapped('child_ids')
            childs |= childs.mapped('child_ids').get_all_children()
        return childs

